import json
import os
import psycopg2
import requests
from psycopg2.extras import DictCursor
from mcp.types import TextContent
import time


from resources import read_file
from settings import CORPUS_PATH_DATABASE, RESUME_FILE_DATABASE

def get_secret_pass():
    stack = os.environ['STACK']
    password = ''
    with open(f'/run/secrets/{stack}_superadmin_pass', 'r') as f:
        password = f.read()
    return password


DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "database"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
    "database": os.getenv("POSTGRES_DB", "migasfree"),
    "user": os.getenv("POSTGRES_USER", "migasfree"),
    "password": get_secret_pass()
}


_conn = None


def get_tables_catalog():
    return read_file(RESUME_FILE_DATABASE)


def get_table_schema(name):
    return read_file(f"{CORPUS_PATH_DATABASE}/{name}.json")






def get_connection():
    global _conn
    if _conn is None or _conn.closed:
        try:
            _conn = psycopg2.connect(**DB_CONFIG)
            _conn.autocommit = False
        except Exception as e:
            print(f"Error establishing database connection: {e}")
            _conn = None
            raise
    return _conn


def validate_sql(statement):
    data = run_sql_select_query(f"EXPLAIN {statement}")
    if isinstance(data, dict) and "ERROR" in data:
        return {"valid": False, "message": f"{data}"}
    return {"valid": True, "message": ""}


def simplify_type_with_length(pg_type: str, type_mod: int) -> str:
    """Simplifica tipos de PostgreSQL incluyendo longitud cuando es relevante"""

    # Calcular longitud real desde type_modifier
    length = None
    if type_mod and type_mod > 0:
        if pg_type in ['varchar', 'bpchar', 'char']:
            length = type_mod - 4  # PostgreSQL añade 4 al valor real
        elif pg_type == 'numeric':
            # Para numeric: ((precision << 16) | scale) + 4
            precision = ((type_mod - 4) >> 16) & 0xffff
            scale = (type_mod - 4) & 0xffff
            if precision > 0:
                length = f"{precision},{scale}" if scale > 0 else str(precision)

    # Mapeo de tipos con longitud
    type_mapping = {
        'int4': 'int',
        'int8': 'bigint',
        'varchar': f'varchar({length})' if length else 'varchar',
        'bpchar': f'char({length})' if length else 'char',
        'char': f'char({length})' if length else 'char',
        'text': 'text',
        'bool': 'boolean',
        'timestamp': 'datetime',
        'timestamptz': 'datetime',
        'date': 'date',
        'numeric': f'decimal({length})' if length else 'decimal',
        'float4': 'float',
        'float8': 'float',
        'uuid': 'uuid'
    }

    return type_mapping.get(pg_type, pg_type)




def run_sql_select_query(query: str,) -> str:
    query_upper = query.upper().strip()

    if not query_upper:
        #return  {"ERROR": "SELECT empty"}
        raise Exception("ERROR: SELECT empty")
    if not (query_upper.startswith("SELECT") or query_upper.startswith("EXPLAIN") or query_upper.startswith("```SQL\nSELECT")):
        #return  {"ERROR": "Solo se permiten sentencias SELECT"}
        raise Exception("ERROR: Only SELECT SQL is allowed")
    if any(k in query_upper for k in ["DROP ", "DELETE ", "UPDATE ", "INSERT ", "ALTER ", "CREATE ", "TRUNCATE "]):
        #return  {"ERROR": "Solo se permiten sentencias SELECT"}
        raise Exception("ERROR: Only SELECT SQL is allowed")

    try:
        conn = get_connection()
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query)
            rows = cur.fetchall()
        return rows

    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except Exception as rollback_e:
                print(f"Error during rollback in run_sql_select_query: {rollback_e}")
                global _conn
                if _conn:
                    _conn.close()
                    _conn = None
        return {"ERROR": str(e)}






#===========================

def tables_catalog() -> str:
    query = """  SELECT
        t.table_name,
        COALESCE(obj_description(c.oid), '') as table_comment,
        COALESCE(
            (SELECT string_agg(
                kcu.column_name || ' -> ' || ccu.table_name || '(' || ccu.column_name || ')',
                ', '
            )
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage ccu
                ON tc.constraint_name = ccu.constraint_name
                AND tc.table_schema = ccu.constraint_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_name = t.table_name
                AND tc.table_schema = 'public'
            ),
            ''
        ) as foreign_keys,
        COALESCE(
            (SELECT string_agg(
                ref_tc.table_name || '(' || ref_kcu.column_name || ') -> ' || ref_ccu.column_name,
                ', '
            )
            FROM information_schema.table_constraints ref_tc
            JOIN information_schema.key_column_usage ref_kcu
                ON ref_tc.constraint_name = ref_kcu.constraint_name
                AND ref_tc.table_schema = ref_kcu.table_schema
            JOIN information_schema.constraint_column_usage ref_ccu
                ON ref_tc.constraint_name = ref_ccu.constraint_name
                AND ref_tc.table_schema = ref_ccu.constraint_schema
            WHERE ref_tc.constraint_type = 'FOREIGN KEY'
                AND ref_ccu.table_name = t.table_name
                AND ref_tc.table_schema = 'public'
            ),
            ''
        ) as referenced_by
    FROM information_schema.tables t
    LEFT JOIN pg_class c ON c.relname = t.table_name
    LEFT JOIN pg_namespace n ON n.oid = c.relnamespace AND n.nspname = 'public'
    WHERE t.table_type = 'BASE TABLE'
        AND t.table_schema = 'public'
        AND t.table_name NOT LIKE 'django_%'
        AND t.table_name NOT LIKE 'auth_%'
    ORDER BY t.table_name;
"""
    return run_sql_select_query(query)


def get_table_fields(table_name: str) -> list:
    query = """
        SELECT
            a.attname AS column_name,
            t.typname AS data_type,
            a.atttypmod AS type_modifier,
            CASE
                WHEN pk.constraint_type = 'PRIMARY KEY' THEN true
                ELSE false
            END AS is_primary_key,
            COALESCE(d.description, '') AS column_description
        FROM
            pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        JOIN pg_attribute a ON a.attrelid = c.oid
        JOIN pg_type t ON a.atttypid = t.oid
        LEFT JOIN pg_description d ON d.objoid = a.attrelid AND d.objsubid = a.attnum
        LEFT JOIN (
            SELECT tc.table_name, kcu.column_name, tc.constraint_type
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
            WHERE tc.constraint_type = 'PRIMARY KEY'
        ) pk ON c.relname = pk.table_name AND a.attname = pk.column_name
        WHERE
            c.relkind = 'r'
            AND a.attnum > 0
            AND n.nspname NOT IN ('pg_catalog', 'information_schema')
            AND n.nspname = 'public'
            AND c.relname = %s
        ORDER BY
            a.attnum;
    """

    def simplify_type_with_length(data_type: str, type_mod: int) -> str:
        if data_type == 'bpchar' or data_type == 'varchar':
            length = type_mod - 4
            return f"{data_type}({length})"
        elif data_type == 'numeric':
            # Puedes parsear más información si es necesario
            return data_type
        else:
            return data_type

    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(query, (table_name,))
            rows = cur.fetchall()

            fields = []

            for row in rows:
                column_name = row[0]
                data_type = row[1]
                type_mod = row[2]
                is_primary_key = row[3]
                column_description = row[4].strip() if row[4] else ''

                field_info = {
                    "name": column_name,
                    "type": simplify_type_with_length(data_type, type_mod),
                    "description": column_description
                }

                if is_primary_key:
                    field_info["primary_key"] = True

                fields.append(field_info)

            return fields

    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except Exception as rollback_e:
                print(f"Error during rollback in get_table_fields: {rollback_e}")
                global _conn
                if _conn:
                    _conn.close()
                    _conn = None
        return json.dumps({"ERROR": str(e)})





def create_schema():

    os.makedirs(CORPUS_PATH_DATABASE, exist_ok=True)

    if not os.path.exists(RESUME_FILE_DATABASE):
        tables = []
        rows = tables_catalog()
        for name,description,foreign_key,referenced_by in rows:
            table={}
            table["table_name"] = name
            if description:
                table["description"] = description
            if foreign_key:
                table["foreign_key"] = foreign_key
            if referenced_by:
                table["referenced_by"] = referenced_by
            tables.append(table)

            schema = {}
            schema["table_name"] = name
            if description:
                schema["description"] = description
            if foreign_key:
                schema["foreign_key"] = foreign_key
            if referenced_by:
                schema["referenced_by"] = referenced_by
            schema["fields"] = get_table_fields(name)
            with open(f"{CORPUS_PATH_DATABASE}/{name}.json","w") as file:
                file.write(json.dumps(schema))

        with open(RESUME_FILE_DATABASE,"w") as file:
            file.write(json.dumps(tables))
