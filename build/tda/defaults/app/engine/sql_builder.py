"""
SQL Queries and Builders for Migasfree TDA Engine
"""
from core.config import FORMULA_PREFIX_DEFAULT

DEFAULT_METRICS_INTERVAL_DAYS = 365

SQL_COMPUTER_ATTRIBUTES = """
    SELECT
        c.id AS computer_id,
        c.name AS computer_name,
        c.project_id,
        COALESCE(p.name, c.project_id::text) AS project_name,
        c.status,
        c.ip_address,
        c.machine,
        CASE WHEN c.machine = 'V' THEN 1.0 ELSE 0.0 END AS machine_type,
        COALESCE(ROUND((EXTRACT(EPOCH FROM (NOW() - c.created_at)) / 86400)::numeric, 1), 0.0) AS computer_age_days,
        COALESCE(ROUND((EXTRACT(EPOCH FROM (NOW() - c.sync_end_date)) / 86400)::numeric, 1), 999.0) AS days_since_last_sync,
        array_agg(DISTINCT sa.attribute_id) FILTER (WHERE sa.attribute_id IS NOT NULL) AS attribute_ids,
        array_agg(DISTINCT ct.serverattribute_id) FILTER (WHERE ct.serverattribute_id IS NOT NULL) AS tag_ids
    FROM client_computer c
    LEFT JOIN core_project p ON p.id = c.project_id
    LEFT JOIN client_computer_sync_attributes sa ON sa.computer_id = c.id
    LEFT JOIN client_computer_tags ct ON ct.computer_id = c.id
    WHERE c.status IN ('assigned', 'reserved', 'unknown')
    GROUP BY c.id, c.name, c.project_id, p.name, c.status, c.ip_address, c.machine, c.created_at, c.sync_end_date
"""


def build_sql_errors(interval_days: int = DEFAULT_METRICS_INTERVAL_DAYS) -> str:
    days = max(1, int(interval_days))
    return f"""
    SELECT
        e.computer_id,
        COUNT(*) AS error_count
    FROM client_error e
    WHERE e.created_at >= NOW() - INTERVAL '{days} days'
    GROUP BY e.computer_id
    """


def build_sql_faults(interval_days: int = DEFAULT_METRICS_INTERVAL_DAYS) -> str:
    days = max(1, int(interval_days))
    return f"""
    SELECT
        f.computer_id,
        COUNT(*) AS fault_count
    FROM client_fault f
    WHERE f.created_at >= NOW() - INTERVAL '{days} days'
    GROUP BY f.computer_id
    """


def build_sql_sync(interval_days: int = DEFAULT_METRICS_INTERVAL_DAYS) -> str:
    days = max(1, int(interval_days))
    return f"""
    SELECT
        s.computer_id,
        COUNT(s.id) AS sync_count,
        COALESCE(
            AVG(CASE WHEN s.created_at > s.start_date THEN EXTRACT(EPOCH FROM (s.created_at - s.start_date)) END),
            AVG(CASE WHEN c.sync_end_date > c.sync_start_date THEN EXTRACT(EPOCH FROM (c.sync_end_date - c.sync_start_date)) END),
            0
        ) AS avg_sync_duration_secs,
        SUM(CASE WHEN s.pms_status_ok = FALSE THEN 1 ELSE 0 END) AS pms_failures
    FROM client_synchronization s
    JOIN client_computer c ON c.id = s.computer_id
    WHERE s.created_at >= NOW() - INTERVAL '{days} days'
    GROUP BY s.computer_id
    """


SQL_COMPUTER_ERRORS = build_sql_errors(DEFAULT_METRICS_INTERVAL_DAYS)
SQL_COMPUTER_FAULTS = build_sql_faults(DEFAULT_METRICS_INTERVAL_DAYS)
SQL_COMPUTER_SYNC = build_sql_sync(DEFAULT_METRICS_INTERVAL_DAYS)

SQL_HARDWARE_METRICS = """
    SELECT
        c.id AS computer_id,
        ROUND(COALESCE(c.ram, 0)::numeric / 1024 / 1024 / 1024, 2) AS ram_gb,
        ROUND(COALESCE(c.storage, 0)::numeric / 1024 / 1024 / 1024, 2) AS disk_gb,
        COALESCE(MAX(hn_cpu.product), c.cpu, 'Unknown CPU') AS cpu_product,
        COALESCE(MAX(COALESCE(hn_cpu.capacity, hn_cpu.clock, hn_cpu.size)) / 1000000, 0) AS cpu_mhz,
        COALESCE(string_agg(DISTINCT CASE WHEN hn_gpu.product IS NOT NULL THEN hn_gpu.product END, ', '), 'None') AS gpus,
        COALESCE(string_agg(DISTINCT CASE WHEN hn_net.product IS NOT NULL THEN hn_net.product END, ', '), 'None') AS network_cards
    FROM client_computer c
    LEFT JOIN hardware_node hn_cpu ON hn_cpu.computer_id = c.id AND hn_cpu.class_name = 'processor'
    LEFT JOIN hardware_node hn_gpu ON hn_gpu.computer_id = c.id AND hn_gpu.class_name = 'display'
    LEFT JOIN hardware_node hn_net ON hn_net.computer_id = c.id AND hn_net.class_name = 'network'
    WHERE c.status IN ('assigned', 'reserved', 'unknown')
    GROUP BY c.id, c.ram, c.storage, c.cpu
"""

SQL_COMPUTER_PACKAGES = """
    SELECT
        ph.computer_id,
        COUNT(DISTINCT ph.package_id) AS total_packages,
        array_agg(DISTINCT ph.package_id) AS package_ids
    FROM client_packagehistory ph
    JOIN client_computer c ON c.id = ph.computer_id
    WHERE ph.uninstall_date IS NULL
      AND c.status IN ('assigned', 'reserved', 'unknown')
    GROUP BY ph.computer_id
"""

SQL_COMPUTER_MIGRATIONS = """
    SELECT
        c.id AS computer_id,
        COUNT(m.id) AS migration_count,
        MAX(m.created_at) AS last_migration_date,
        COALESCE(EXTRACT(EPOCH FROM (NOW() - MAX(m.created_at))) / 86400, 999.0) AS days_since_last_migration,
        COALESCE(MAX(m.project_id), c.project_id) AS last_migrated_project_id
    FROM client_computer c
    LEFT JOIN client_migration m ON m.computer_id = c.id
    WHERE c.status IN ('assigned', 'reserved', 'unknown')
    GROUP BY c.id, c.project_id
"""

SQL_ALL_PACKAGES = """
    SELECT DISTINCT id, name FROM core_package ORDER BY id
"""

SQL_ATTRIBUTE_NAMES = """
    SELECT
        a.id,
        a.property_att_id,
        a.value,
        p.prefix AS property_prefix,
        p.name AS property_name,
        CONCAT(p.prefix, '-', a.value) AS name
    FROM core_attribute a
    JOIN core_property p ON p.id = a.property_att_id
    WHERE a.id <> 1
"""


def build_sql_all_attributes(ids: list, union_scope_sql: str = None) -> str:
    """
    Build the SQL query for all formula attributes filtered by property_att_id
    and optionally restricted to attributes present on computers in scope.
    """
    if not ids:
        return "SELECT id FROM core_attribute WHERE 1=0"
    conditions = " OR ".join(f"a.property_att_id={i}" for i in ids)
    scope_filter = f"AND c.id IN ({union_scope_sql})" if union_scope_sql else ""
    return f"""
    SELECT DISTINCT a.id
    FROM core_attribute a
    WHERE ({conditions}) AND a.id <> 1
      AND (
          a.id IN (
              SELECT sa.attribute_id FROM client_computer_sync_attributes sa
              JOIN client_computer c ON c.id = sa.computer_id
              WHERE c.status IN ('assigned', 'reserved', 'unknown') {scope_filter}
          )
          OR a.id IN (
              SELECT ct.serverattribute_id FROM client_computer_tags ct
              JOIN client_computer c ON c.id = ct.computer_id
              WHERE c.status IN ('assigned', 'reserved', 'unknown') {scope_filter}
          )
      )
    ORDER BY a.id
"""
