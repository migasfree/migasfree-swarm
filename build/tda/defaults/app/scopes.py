"""
Scope helpers for the TDA service.

A migasfree Scope (core_scope) is an attribute-based filter: a computer
belongs to a scope when it has at least one included attribute and none of
the excluded ones, optionally restricted to a Domain. This module builds the
SQL used by the engine (dataset restriction) and by the API (scope picker).

Only lightweight imports here: the heavy database access is resolved lazily
via `database.query_dataframe` so the module stays importable without a DB.
"""

import logging

logger = logging.getLogger("migasfree-tda")

# Same status set as SQL_COMPUTER_ATTRIBUTES (productive computers)
SCOPE_STATUS = "('assigned', 'reserved', 'unknown')"

SCOPE_SELECT = """
    SELECT DISTINCT computer_id
    FROM client_computer_sync_attributes
    INNER JOIN client_computer ON client_computer.id = client_computer_sync_attributes.computer_id
    WHERE attribute_id IN (
        SELECT attribute_id
        FROM {table}_included_attributes
        WHERE {key}_id = {id}
    ) AND client_computer.status IN {status}
    EXCEPT
    SELECT DISTINCT computer_id
    FROM client_computer_sync_attributes
    WHERE attribute_id IN (
        SELECT attribute_id
        FROM {table}_excluded_attributes
        WHERE {key}_id = {id}
    )
"""


def _scope_select(prefix: str, key: str, id: int) -> str:
    """Subquery of the computers matching an included/excluded attribute set."""
    return SCOPE_SELECT.format(
        table=prefix, key=key, id=id, status=SCOPE_STATUS
    )


def scope_computer_sql(scope_id: int, domain_id=None) -> str:
    """
    Subquery SQL of the computers belonging to a scope.

    A computer is in the scope when it has at least one included attribute
    and no excluded attribute. When the scope has a domain, the result is
    intersected with the same pattern over the domain attributes (matching
    Scope.related_objects).
    """
    sql = _scope_select("core_scope", "scope", scope_id)
    if domain_id:
        domain_sql = _scope_select("core_domain", "domain", domain_id)
        sql = f"({sql} INTERSECT {domain_sql})"
    return f"({sql})"


def _clean_int(value):
    """Coerce a DB value (possibly pandas NaN) to int, or None for empty."""
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError, OverflowError):
        return None


def _clean_str(value):
    """Coerce a DB value (possibly pandas NaN) to str, or None for empty."""
    if value is None:
        return None
    text = str(value)
    return text if text.strip() and text.lower() != "nan" else None


def get_scope_domain_map(scope_ids) -> dict:
    """
    Resolve the domain of each scope: {scope_id: domain_id|None}.

    Non-existent scope ids are simply absent from the map.
    """
    from database import query_dataframe

    scope_ids = [int(s) for s in scope_ids if str(s).strip().isdigit() and int(s) > 0]
    if not scope_ids:
        return {}
    placeholders = ", ".join(str(s) for s in scope_ids)
    df = query_dataframe(
        f"SELECT id, domain_id FROM core_scope WHERE id IN ({placeholders})"
    )
    if df.empty:
        return {}
    domain_map = {}
    for _, row in df.iterrows():
        domain_map[int(row["id"])] = _clean_int(row.get("domain_id"))
    return domain_map


def union_scope_sql(scope_ids, domain_map) -> str:
    """
    UNION of the scope subqueries for the given scope ids.

    Returns None when there are no scope ids. Scope ids missing from the
    domain map contribute an empty set (their subquery selects nothing).
    """
    if not scope_ids:
        return None
    parts = []
    for scope_id in scope_ids:
        domain_id = domain_map.get(int(scope_id))
        parts.append(scope_computer_sql(scope_id, domain_id))
    return "\nUNION\n".join(parts)


def count_scope(scope_id: int, domain_id=None) -> int:
    """Number of computers in a scope (used to display the scope picker)."""
    from database import query_dataframe

    sql = f"SELECT COUNT(*) FROM {scope_computer_sql(scope_id, domain_id)} t"
    df = query_dataframe(sql)
    return int(df.iloc[0, 0])


def _user_scope_where(username: str) -> tuple:
    """
    WHERE clause + params restricting scopes to the authenticated user.

    The scope owner (core_scope.user_id) points at the user profile row,
    whose user_ptr_id matches auth_user.id, so the username lookup goes
    through auth_user (parameterized, never interpolated).
    """
    return (
        "s.user_id = (SELECT id FROM auth_user WHERE username = %s)",
        (username,),
    )


def available_scopes(username: str) -> list:
    """
    Scopes owned by the authenticated user for the settings picker.

    Returns a list of dicts:
        {id, name, domain_id, domain_name, computer_count, attribute_count}

    Tolerant to a missing database: returns [] and logs a warning.
    """
    from database import query_dataframe

    try:
        where_sql, params = _user_scope_where(username)
        df = query_dataframe(
            f"""
            SELECT
                s.id,
                s.name,
                s.domain_id,
                d.name AS domain_name,
                (SELECT COUNT(*) FROM core_scope_included_attributes i WHERE i.scope_id = s.id)
                    AS attribute_count
            FROM core_scope s
            LEFT JOIN core_domain d ON d.id = s.domain_id
            WHERE {where_sql}
            ORDER BY s.name
            """,
            params=params,
        )
        if df.empty:
            return []
        scopes = []
        for _, row in df.iterrows():
            scope_id = int(row["id"])
            domain_id = _clean_int(row.get("domain_id"))
            try:
                computer_count = count_scope(scope_id, domain_id)
            except Exception as exc:
                logger.warning(f"Could not count computers of scope {scope_id}: {exc}")
                computer_count = 0
            scopes.append(
                {
                    "id": scope_id,
                    "name": str(row["name"]),
                    "domain_id": domain_id,
                    "domain_name": _clean_str(row.get("domain_name")),
                    "computer_count": computer_count,
                    "attribute_count": _clean_int(row.get("attribute_count")) or 0,
                }
            )
        return scopes
    except Exception as exc:
        logger.warning(f"Could not fetch available scopes (DB may be unavailable): {exc}")
        return []
