"""
TDA Engine: Topological Data Analysis core module for Migasfree.

Implements the Mapper algorithm and Persistent Homology pipelines
described in docs/tda.md.
"""

import os
import re
import logging
import json
from datetime import datetime
from collections import Counter

import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform
from sklearn.base import BaseEstimator
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN, KMeans, AgglomerativeClustering

import kmapper as km

from lens_store import (
    load_lens,
    validate_lens,
    resolve_lens_output_path,
    NODE_LABELS,
    DATASET_METRICS,
    COVER_OVERLAP_DEFAULT,
)

import scopes

logger = logging.getLogger("migasfree-tda")


# ---------------------------------------------------------------------------
# Adaptive Mapper parameters
# ---------------------------------------------------------------------------

def resolve_n_cubes(n_samples, is_2d, n_cubes_override=None):
    """
    Resolution of the Mapper cover. An explicit override wins; otherwise the
    value follows the adaptive thresholds used by the engine (for 2D lenses
    n_cubes is per dimension, so the total number of cubes is n_cubes^2).
    """
    if n_cubes_override:
        return int(n_cubes_override)
    if is_2d:
        if n_samples < 50:
            return 5
        if n_samples < 500:
            return 8
        if n_samples < 2000:
            return 10
        return 12
    if n_samples < 100:
        return 8
    if n_samples < 1000:
        return 12
    return 15


# ---------------------------------------------------------------------------
# SQL Queries for data extraction
# ---------------------------------------------------------------------------

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

DEFAULT_METRICS_INTERVAL_DAYS = 365


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

TDA_CONFIG_PATH = "/data/tda/config.json"
FORMULA_PREFIX_DEFAULT = [3, 5]

DEFAULT_LENS_COLORS = {
    "health": {"columns": ["error_count"], "label": "Error Count", "kind": "continuous"},
    "obsolescence": {"columns": ["ram_gb"], "label": "RAM (GB)", "kind": "continuous"},
    "sync": {"columns": ["avg_sync_duration_secs"], "label": "Avg Sync Duration (secs)", "kind": "continuous"},
    "software": {"columns": ["total_packages"], "label": "Total Installed Packages", "kind": "continuous"},
    "migration": {"columns": ["migration_count"], "label": "Migrations Count", "kind": "continuous"},
    "diversity": {"columns": ["jaccard_outlier_score"], "label": "Configuration Outlier Score (Mean Jaccard Distance)", "kind": "continuous"},
}

DEFAULT_LENS_COLOR = {"columns": ["error_count"], "label": "Error Count", "kind": "continuous"}

COLOR_KINDS = ("continuous", "categorical")


def get_formula_prefix_ids() -> list:
    """
    Read the formula prefix property_att IDs from the TDA config file.

    Returns a list of integer IDs to use in the SQL filter for
    SQL_ALL_ATTRIBUTES. Falls back to FORMULA_PREFIX_DEFAULT if the
    config file does not exist or cannot be parsed.

    Config file: /data/tda/config.json
    Example: { "formula_prefix_ids": [3, 5] }
    """
    try:
        if os.path.isfile(TDA_CONFIG_PATH):
            with open(TDA_CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            ids = cfg.get("formula_prefix_ids", FORMULA_PREFIX_DEFAULT)
            # Validate: must be a non-empty list of positive integers
            ids = [int(i) for i in ids if str(i).strip().isdigit() and int(i) > 0]
            if ids:
                return ids
    except Exception as exc:
        logger.warning(f"Could not read TDA config from {TDA_CONFIG_PATH}: {exc}")
    return list(FORMULA_PREFIX_DEFAULT)


def get_lens_colors() -> dict:
    """
    Read the per-lens coloring configuration from the TDA config file.

    Returns a dict mapping lens name -> {"columns": [...], "label": "...", "kind": "..."}.
    Entries from the config file override the defaults for that lens; lenses
    not present fall back to DEFAULT_LENS_COLORS / DEFAULT_LENS_COLOR.
    kind is "continuous" (gradient coloring) or "categorical" (per-category colors).

    Config file: /data/tda/config.json
    Example:
        { "lens_colors": {
              "health": { "columns": ["fault_count"], "label": "Fault Count" }
          } }
    """
    colors = {k: dict(v) for k, v in DEFAULT_LENS_COLORS.items()}
    try:
        if os.path.isfile(TDA_CONFIG_PATH):
            with open(TDA_CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            raw = cfg.get("lens_colors", {})
            if isinstance(raw, dict):
                for lens, entry in raw.items():
                    if not isinstance(entry, dict):
                        continue
                    fallback = DEFAULT_LENS_COLORS.get(lens, DEFAULT_LENS_COLOR)
                    columns = entry.get("columns") or fallback["columns"]
                    if not isinstance(columns, (list, tuple)):
                        columns = [columns]
                    columns = [str(c) for c in columns if str(c).strip()]
                    if not columns:
                        columns = fallback["columns"]
                    entry_kind = entry.get("kind")
                    if entry_kind is not None and str(entry_kind) in COLOR_KINDS:
                        kind = str(entry_kind)
                    elif "project_encoded" in columns:
                        kind = "categorical"
                    else:
                        kind = str(fallback.get("kind") or "continuous")
                    colors[lens] = {
                        "columns": list(columns),
                        "label": str(entry.get("label") or fallback["label"]),
                        "kind": kind,
                    }
    except Exception as exc:
        logger.warning(f"Could not read TDA config (lens_colors) from {TDA_CONFIG_PATH}: {exc}")
    return colors


def build_sql_all_attributes(ids: list, union_scope_sql: str = None) -> str:
    """
    Build the SQL query for all formula attributes filtered by property_att_id
    and optionally restricted to attributes present on computers in scope.

    Args:
        ids: list of property_att_id integers to include.
            An empty list means NO attribute dimensions are included
            in the feature matrix.
        union_scope_sql: optional SQL subquery of computer IDs matching the scope.

    Returns:
        SQL string with WHERE clause dynamically generated.
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

def build_feature_matrix(
    db,
    formula_prefix_ids=None,
    scope_ids=None,
    metric_columns=None,
    metrics_interval_days=None,
):
    """
    Build a numerical feature matrix from the migasfree database.

    Each row = one computer, columns = binary attribute/tag vector +
    selected metric columns.

    Args:
        db: unused (kept for compatibility).
        formula_prefix_ids: list of core_property IDs whose attributes are
            included. None = read from the global config (per-lens override).
        scope_ids: restrict analysis to these scope IDs (union of scopes);
            empty = all. None = no scope filter.
        metric_columns: list of numeric metric columns (from
            lens_store.DATASET_METRICS) to include in the feature matrix.
            None = all metrics (backward compatible). [] = no metric columns.
        metrics_interval_days: number of days to look back for event metrics
            (errors, faults, syncs). None = DEFAULT_METRICS_INTERVAL_DAYS (365).

    Returns (DataFrame with computer metadata, numpy feature matrix).
    """
    from database import query_dataframe

    logger.info("Extracting computer attributes...")
    # Per-lens override: fall back to the global config when not provided
    if formula_prefix_ids is None:
        formula_prefix_ids = get_formula_prefix_ids()
    if scope_ids is None:
        scope_ids = []
    if metric_columns is None:
        metric_columns = list(DATASET_METRICS)
    metric_cols = [c for c in metric_columns if c in DATASET_METRICS]

    if metrics_interval_days is None:
        metrics_interval_days = DEFAULT_METRICS_INTERVAL_DAYS
    try:
        metrics_interval_days = int(metrics_interval_days)
    except (ValueError, TypeError):
        metrics_interval_days = DEFAULT_METRICS_INTERVAL_DAYS
    if metrics_interval_days <= 0:
        metrics_interval_days = DEFAULT_METRICS_INTERVAL_DAYS

    conditions = ["c.status IN ('assigned', 'reserved', 'unknown')"]
    union_sql = None
    if scope_ids:
        domain_map = scopes.get_scope_domain_map(scope_ids)
        union_sql = scopes.union_scope_sql(scope_ids, domain_map)
        if union_sql:
            conditions.append(f"c.id IN ({union_sql})")
        logger.info(f"Filtering computers by scope_ids: {scope_ids}")
    sql_computers = SQL_COMPUTER_ATTRIBUTES.replace(
        "WHERE c.status IN ('assigned', 'reserved', 'unknown')",
        "WHERE " + " AND ".join(conditions),
    )
    df_computers = query_dataframe(sql_computers)
    if df_computers.empty:
        logger.warning("No computers found in database")
        return pd.DataFrame(), np.array([])

    logger.info(f"Found {len(df_computers)} computers")

    # Get the full list of attribute IDs for binary encoding
    # Per-lens formula prefix IDs (fallback to /data/tda/config.json)
    logger.info(f"Using formula prefix property_att_ids: {formula_prefix_ids}")
    sql_attrs = build_sql_all_attributes(formula_prefix_ids, union_sql)
    df_attrs = query_dataframe(sql_attrs)
    all_attr_ids = sorted(df_attrs["id"].tolist()) if not df_attrs.empty else []

    # Map every attribute id in the fleet to "PREFIX-value" (e.g. NET-10.0.3.0/24)
    # so grouping-reason annotations always show a readable name.
    attr_names = {}
    attr_property = {}
    prefix_names = {}
    prefix_to_name = {}
    try:
        df_attr_names = query_dataframe(SQL_ATTRIBUTE_NAMES)
        if not df_attr_names.empty:
            for _, row in df_attr_names.iterrows():
                try:
                    attr_names[int(row["id"])] = str(row["name"])
                except (ValueError, TypeError):
                    continue
                if "property_att_id" in df_attr_names.columns:
                    try:
                        attr_property[int(row["id"])] = int(row["property_att_id"])
                    except (ValueError, TypeError):
                        continue
                if "property_att_id" in df_attr_names.columns:
                    try:
                        pid = int(row["property_att_id"])
                        p_name = str(row["property_name"]) if "property_name" in df_attr_names.columns and pd.notnull(row.get("property_name")) else str(row.get("property_prefix", pid))
                        prefix_names[pid] = p_name
                        if "property_prefix" in df_attr_names.columns and pd.notnull(row.get("property_prefix")):
                            prefix_to_name[str(row["property_prefix"])] = p_name
                    except (ValueError, TypeError):
                        continue
    except Exception as exc:
        logger.warning(f"Could not load attribute names: {exc}")

    # Build binary attribute vector per computer
    attr_matrix = np.zeros((len(df_computers), len(all_attr_ids)), dtype=np.float32)
    attr_id_to_idx = {aid: idx for idx, aid in enumerate(all_attr_ids)}

    for row_pos, (_, row) in enumerate(df_computers.iterrows()):
        attr_ids = row.get("attribute_ids")
        if isinstance(attr_ids, (list, tuple, np.ndarray)):
            for aid in attr_ids:
                if aid in attr_id_to_idx:
                    attr_matrix[row_pos, attr_id_to_idx[aid]] = 1.0
        tag_ids = row.get("tag_ids")
        if isinstance(tag_ids, (list, tuple, np.ndarray)):
            for tid in tag_ids:
                if tid in attr_id_to_idx:
                    attr_matrix[row_pos, attr_id_to_idx[tid]] = 1.0

    # Merge error/fault/sync/hardware/packages/migrations metrics
    df_errors = query_dataframe(build_sql_errors(metrics_interval_days))
    df_faults = query_dataframe(build_sql_faults(metrics_interval_days))
    df_sync = query_dataframe(build_sql_sync(metrics_interval_days))
    df_hardware = query_dataframe(SQL_HARDWARE_METRICS)
    df_packages = query_dataframe(SQL_COMPUTER_PACKAGES)
    df_migrations = query_dataframe(SQL_COMPUTER_MIGRATIONS)

    df_computers = df_computers.merge(df_errors, on="computer_id", how="left")
    df_computers = df_computers.merge(df_faults, on="computer_id", how="left")
    df_computers = df_computers.merge(df_sync, on="computer_id", how="left")
    df_computers = df_computers.merge(df_hardware, on="computer_id", how="left")
    df_computers = df_computers.merge(df_packages, on="computer_id", how="left")
    df_computers = df_computers.merge(df_migrations, on="computer_id", how="left")

    # Build binary package matrix
    df_all_pkgs = query_dataframe(SQL_ALL_PACKAGES)
    all_pkg_ids = sorted(df_all_pkgs["id"].tolist()) if not df_all_pkgs.empty else []
    pkg_id_to_idx = {pid: idx for idx, pid in enumerate(all_pkg_ids)}
    pkg_matrix = np.zeros((len(df_computers), len(all_pkg_ids)), dtype=np.float32)

    for row_pos, (_, row) in enumerate(df_computers.iterrows()):
        pkg_ids = row.get("package_ids")
        if isinstance(pkg_ids, (list, tuple, np.ndarray)):
            for pid in pkg_ids:
                if pid in pkg_id_to_idx:
                    pkg_matrix[row_pos, pkg_id_to_idx[pid]] = 1.0

    df_computers["_pkg_matrix"] = list(pkg_matrix)
    # Store attribute matrix for diversity lens (config divergence)
    df_computers["_attr_matrix"] = list(attr_matrix)

    # Fill NaN metrics with 0 / defaults (only the selected metric columns)
    for col in metric_cols:
        if col not in df_computers.columns:
            df_computers[col] = 0.0
        df_computers[col] = pd.to_numeric(df_computers[col], errors="coerce").fillna(0.0)

    # Encode project_id as numeric for optional categorical coloring only
    le = LabelEncoder()
    df_computers["project_encoded"] = le.fit_transform(
        df_computers["project_id"].fillna(-1).astype(str)
    )

    # Final feature matrix: strictly user-selected attributes + selected metrics
    parts = []
    if attr_matrix.shape[1] > 0:
        parts.append(attr_matrix)
    if metric_cols:
        metrics = df_computers[metric_cols].values.astype(np.float32)
        parts.append(metrics)

    if parts:
        feature_matrix = np.hstack(parts)
    else:
        # Fallback if neither attributes nor metrics were selected
        feature_matrix = np.ones((len(df_computers), 1), dtype=np.float32)

    # Remove zero-variance columns
    variances = feature_matrix.var(axis=0)
    nonzero_mask = variances > 0
    if nonzero_mask.sum() > 0:
        feature_matrix = feature_matrix[:, nonzero_mask]

    logger.info(
        f"Feature matrix: {feature_matrix.shape[0]} computers × "
        f"{feature_matrix.shape[1]} features"
    )

    # Keep the attribute id→name map for grouping-reason annotations,
    # and the exact attribute set used in the matrix (so the reason-for-grouping
    # only shows attributes that actually participate in the computation)
    df_computers.attrs["attr_names"] = attr_names
    df_computers.attrs["matrix_attr_ids"] = set(all_attr_ids)
    df_computers.attrs["attr_id_to_idx"] = dict(attr_id_to_idx)
    df_computers.attrs["attr_property"] = attr_property
    df_computers.attrs["prefix_names"] = prefix_names
    df_computers.attrs["prefix_to_name"] = prefix_to_name

    return df_computers, feature_matrix


def estimate_matrix_counts(formula_prefix_ids=None, scope_ids=None, metric_columns=None):
    """
    Estimate the N x D feature matrix dimensions without building it.

    Mirrors the filtering logic of ``build_feature_matrix`` but only
    runs cheap COUNT queries. ``metric_columns=None`` means "all metrics".
    """
    from database import query_dataframe

    def _ids(values):
        if values is None:
            return []
        if isinstance(values, (list, tuple)):
            return [int(i) for i in values if str(i).strip().lstrip("-").isdigit() and int(i) > 0]
        return []

    prefix_ids = _ids(formula_prefix_ids)
    scope_ids = _ids(scope_ids)

    known_metrics = set(DATASET_METRICS)
    if metric_columns is None:
        n_metric = len(DATASET_METRICS)
    else:
        n_metric = len([m for m in metric_columns if m in known_metrics])

    conds = ["c.status IN ('assigned', 'reserved', 'unknown')"]
    union_sql = None
    if scope_ids:
        domain_map = scopes.get_scope_domain_map(scope_ids)
        union_sql = scopes.union_scope_sql(scope_ids, domain_map)
        if union_sql:
            conds.append(f"c.id IN ({union_sql})")
    n = int(
        query_dataframe(
            "SELECT COUNT(*) FROM client_computer c WHERE " + " AND ".join(conds)
        ).iloc[0, 0]
    )

    if prefix_ids and n > 0:
        sql_attrs = build_sql_all_attributes(prefix_ids, union_sql)
        d_attr = int(
            query_dataframe(f"SELECT COUNT(*) FROM ({sql_attrs}) _attr_q").iloc[0, 0]
        )
    else:
        d_attr = 0

    d_max = d_attr + n_metric
    return {
        "n": n,
        "d_attr": d_attr,
        "n_metric": n_metric,
        "d_max": d_max,
        "estimated_bytes": n * d_max * 4,
    }


_ATTR_COL_RE = re.compile(r"^attr_(\d+)$")
_PREFIX_COL_RE = re.compile(r"^prefix_(\d+)$")


def _attr_color_vector(df_computers, attr_id):
    """
    Boolean presence vector (shape (N,)) for one attribute dimension of the
    N×D feature matrix. The binary attribute matrix is kept in the
    ``_attr_matrix`` column of df_computers; ``attr_id_to_idx`` (stored in
    df_computers.attrs by build_feature_matrix) maps attribute id → column.
    """
    idx_map = getattr(df_computers, "attrs", {}).get("attr_id_to_idx")
    if not idx_map or "_attr_matrix" not in df_computers.columns:
        return None
    idx = idx_map.get(int(attr_id))
    if idx is None:
        return None
    mat = np.array(df_computers["_attr_matrix"].tolist(), dtype=np.float32)
    return mat[:, idx]


def _prefix_labels(df_computers, property_id):
    """
    Per-computer category label for a core_property (prefix), e.g. "CTX-aula".

    The label is the readable "PREFIX-value" of the most specific attribute
    (attribute or tag) the computer has for the property. A computer can carry
    both a generic parent value and a more specific child of the same property
    (e.g. "CTX-AYTOZAR" + "CTX-RYS.AYTOZAR"); the deepest value wins. Missing
    values are empty strings. Returns None when the property is not part of
    the fleet (or the attribute catalogs are unavailable).
    """
    attr_property = getattr(df_computers, "attrs", {}).get("attr_property") or {}
    attr_names = getattr(df_computers, "attrs", {}).get("attr_names") or {}
    if not attr_property:
        return None
    labels = []
    seen = False
    for _, row in df_computers.iterrows():
        label = ""
        best_len = -1
        for col in ("attribute_ids", "tag_ids"):
            ids = row.get(col)
            if not isinstance(ids, (list, tuple, np.ndarray)):
                continue
            for aid in ids:
                if aid is None or (isinstance(aid, float) and np.isnan(aid)):
                    continue
                try:
                    aid = int(aid)
                except (ValueError, TypeError):
                    continue
                if attr_property.get(aid) == int(property_id):
                    name = attr_names.get(aid, f"attr-{aid}")
                    # Deepest attribute value (children embed the parent name,
                    # e.g. "RYS.AYTOZAR" under "AYTOZAR") is the most specific.
                    if len(name) > best_len:
                        label = name
                        best_len = len(name)
                    seen = True
        labels.append(label)
    if not seen:
        return None
    return labels


def _resolve_color_data(df_computers, column_list):
    """
    Build the color signal for a column list.

    Returns (color_data, resolved_columns, color_labels) or None when no
    column resolves. Supported column kinds:
      - df_computers metric columns (numeric, summed when several)
      - "attr_<id>": boolean attribute dimension of the N×D matrix
      - "prefix_<property_id>": categorical color by the concrete values of a
        core_property (prefix); wins over the other kinds.

    color_labels (only set for prefix colors) carries the readable per-row
    category name used by _graph_to_json to build color_categories.
    """
    prefix_ids = []
    for c in column_list:
        m = _PREFIX_COL_RE.match(str(c))
        if m:
            prefix_ids.append(int(m.group(1)))

    # Prefix-based coloring has priority (readable per-value categorical colors)
    if prefix_ids:
        for pid in prefix_ids:
            labels = _prefix_labels(df_computers, pid)
            if labels is not None:
                le = LabelEncoder()
                encoded = le.fit_transform(labels).astype(np.float64)
                return encoded, [f"prefix_{pid}"], labels

    df_cols = [c for c in column_list if c in df_computers.columns]
    attr_ids = []
    for c in column_list:
        m = _ATTR_COL_RE.match(str(c))
        if m and _attr_color_vector(df_computers, int(m.group(1))) is not None:
            attr_ids.append(int(m.group(1)))

    parts = []
    if df_cols:
        if len(df_cols) == 1:
            parts.append(pd.to_numeric(df_computers[df_cols[0]], errors="coerce").fillna(0.0).values)
        else:
            parts.append(
                df_computers[df_cols].apply(pd.to_numeric, errors="coerce").fillna(0.0).sum(axis=1).values
            )
    for aid in attr_ids:
        parts.append(_attr_color_vector(df_computers, aid))
    if not parts:
        return None

    color_data = parts[0] if len(parts) == 1 else sum(parts)
    return color_data, df_cols + [f"attr_{aid}" for aid in attr_ids], None


def _resolve_lens_color(lens_name, df_computers, spec=None):
    """
    Resolve the coloring metric for a lens.

    Priority:
      1. Per-lens descriptor color (spec["draw"]["color"])
      2. Global config lens_colors (legacy /data/tda/config.json)
      3. Built-in default for the lens / project_encoded fallback

    Columns may be df_computers metric columns, boolean attribute dimensions
    of the N×D matrix ("attr_<id>") or a core_property prefix ("prefix_<id>",
    which colors categorically by each concrete value of that prefix).

    Returns (color_data, label, kind, columns, color_labels) where kind is
    "continuous" or "categorical"; color_labels is a per-row category name
    list (prefix colors only, None otherwise).
    """
    draw_color = None
    if spec is not None and isinstance(spec.get("draw"), dict):
        draw_color = spec["draw"].get("color")

    if isinstance(draw_color, dict):
        cfg = draw_color
        columns = cfg.get("columns") or []
        raw_label = cfg.get("label")
        explicit_label = raw_label is not None and bool(str(raw_label).strip())
        label = str(raw_label).strip() if explicit_label else DEFAULT_LENS_COLOR["label"]
        kind = cfg.get("kind") or ("categorical" if "project_encoded" in columns else "continuous")
        fallback = DEFAULT_LENS_COLOR
    else:
        cfg = get_lens_colors().get(lens_name) or {}
        fallback = DEFAULT_LENS_COLORS.get(lens_name, DEFAULT_LENS_COLOR)
        columns = cfg.get("columns") or fallback["columns"]
        raw_label = cfg.get("label")
        explicit_label = raw_label is not None and bool(str(raw_label).strip())
        label = str(raw_label).strip() if explicit_label else fallback["label"]
        kind = cfg.get("kind") or fallback.get("kind") or "continuous"

    attr_names = getattr(df_computers, "attrs", {}).get("attr_names", {})
    prefix_names = getattr(df_computers, "attrs", {}).get("prefix_names", {})

    candidates = [
        columns,
        fallback["columns"],
        DEFAULT_LENS_COLOR["columns"],
        columns[:1] or ["project_encoded"],
    ]

    color_data, resolved_columns, color_labels = None, [], None
    for idx, column_list in enumerate(candidates):
        result = _resolve_color_data(df_computers, column_list)
        if result is None:
            continue
        color_data, resolved_columns, color_labels = result
        if idx == 1:
            label = fallback["label"]
            kind = fallback.get("kind", "continuous")
        elif idx == 2:
            label = DEFAULT_LENS_COLOR["label"]
            kind = DEFAULT_LENS_COLOR["kind"]
        break

    if color_data is None:
        return None, label, kind, list(resolved_columns), None

    # Label: name attribute/prefix colors from the catalogs unless the user
    # explicitly provided a custom label.
    if resolved_columns and not explicit_label:
        pm = _PREFIX_COL_RE.match(str(resolved_columns[0]))
        if pm and len(resolved_columns) == 1:
            label = prefix_names.get(int(pm.group(1)), label)
        else:
            attr_ids = [int(m.group(1)) for c in resolved_columns if (m := _ATTR_COL_RE.match(str(c)))]
            if attr_ids and not any(c in df_computers.columns for c in resolved_columns):
                if len(attr_ids) == 1:
                    label = attr_names.get(attr_ids[0], label)
                elif attr_names:
                    label = " + ".join(attr_names.get(aid, f"attr-{aid}") for aid in attr_ids)
                else:
                    label = ", ".join(f"attr_{aid}" for aid in attr_ids)

    # Prefix colors are inherently categorical (one color per concrete value)
    if color_labels is not None:
        kind = "categorical"
    elif kind not in COLOR_KINDS:
        kind = "categorical" if "project_encoded" in resolved_columns or any(_ATTR_COL_RE.match(str(c)) for c in resolved_columns) else "continuous"

    return color_data, label, kind, list(resolved_columns), color_labels


def apply_lens_projection(df_computers, feature_matrix, X_scaled, spec):
    """
    Compute the lens projection for a declarative lens descriptor.

    Supported lens types (lens_store.LENS_TYPES):
      - identity:    1–2 raw numeric columns from df_computers (standardized).
      - pca:         PCA over the whole normalized feature space (1 or 2
                     components, from spec.lens.components).
      - mds_jaccard: Jaccard distance on the binary attribute/package matrix
                     + MDS (2D).

    Every projection falls back to PCA when the requested data has no variance.

    Args:
        df_computers: DataFrame with computer metadata (mutated in place to
                      cache drift scores).
        feature_matrix: numpy array (n_computers × n_features).
        X_scaled: normalized feature matrix.
        spec: validated lens descriptor dict.

    Returns:
        numpy array with the lens projection (1D or 2D).
    """
    lens_name = spec.get("name", "custom")
    lens_cfg = spec.get("lens") or {}
    projection = lens_cfg.get("type", "pca")
    components = lens_cfg.get("components", 2)
    metric_columns = lens_cfg.get("metric_columns") or []
    matrix_source = lens_cfg.get("matrix_source") or "attributes"
    n_samples = len(df_computers)

    def _pca(n_components):
        n_comp = min(n_components, X_scaled.shape[1]) if X_scaled.shape[1] > 0 else 1
        if X_scaled.shape[1] > 0:
            return PCA(n_components=n_comp).fit_transform(X_scaled)
        return np.zeros((n_samples, 1))

    def _pca_fallback():
        return _pca(2)

    if projection == "identity":
        columns = metric_columns[:2]
        for c in columns:
            if c not in df_computers.columns:
                df_computers[c] = 0.0
        present = [c for c in columns if c in df_computers.columns]
        if not present:
            return _pca_fallback()
        if len(present) == 1:
            values = df_computers[present[0]].values.astype(np.float32)
            if values.size > 0 and values.var() > 0:
                return StandardScaler().fit_transform(values.reshape(-1, 1))
            return _pca_fallback()
        metrics = df_computers[present].values.astype(np.float32)
        variances = metrics.var(axis=0)
        valid = variances > 0
        if valid.sum() < 2:
            return _pca_fallback()
        return StandardScaler().fit_transform(metrics[:, valid])
    elif projection == "pca":
        return _pca(components)
    elif projection == "mds_jaccard":
        if matrix_source == "packages":
            if "_pkg_matrix" in df_computers.columns:
                mat = np.array(df_computers["_pkg_matrix"].tolist(), dtype=np.float32)
            else:
                mat = feature_matrix
            drift_col = "software_drift_score"
        else:
            if "_attr_matrix" in df_computers.columns:
                mat = np.array(df_computers["_attr_matrix"].tolist(), dtype=np.float32)
            else:
                mat = feature_matrix
            drift_col = "jaccard_outlier_score"
        df_computers[drift_col] = 0.0
        if mat.size > 0 and mat.shape[1] > 0 and mat.sum() > 0:
            try:
                if n_samples >= 3:
                    distances = pdist(mat, metric="jaccard")
                    dist_matrix = squareform(distances)
                    from sklearn.manifold import MDS
                    mds = MDS(n_components=2, dissimilarity="precomputed", random_state=42)
                    lens = mds.fit_transform(dist_matrix)
                    df_computers[drift_col] = dist_matrix.mean(axis=1)
                else:
                    lens = PCA(n_components=min(2, max(1, mat.shape[1]))).fit_transform(mat)
            except Exception as ex:
                logger.error(f"Error computing MDS Jaccard for lens '{lens_name}': {ex}. Falling back to PCA.")
                lens = _pca_fallback()
        else:
            lens = _pca_fallback()
    elif projection == "multi_lens":
        # 1. Continuous numeric submatrix -> PCA (1 component)
        dataset_cfg = spec.get("dataset") or {}
        num_metric_cols = dataset_cfg.get("metric_columns")
        if num_metric_cols is None:
            num_metric_cols = list(DATASET_METRICS)
        valid_metric_cols = [c for c in num_metric_cols if c in df_computers.columns]

        lens_num = None
        num_scaled = None
        if valid_metric_cols:
            num_data = df_computers[valid_metric_cols].values.astype(np.float32)
            variances = num_data.var(axis=0)
            valid_idx = variances > 0
            if valid_idx.sum() > 0:
                num_scaled = StandardScaler().fit_transform(num_data[:, valid_idx])
                lens_num = PCA(n_components=1).fit_transform(num_scaled)

        # 2. Binary discrete submatrix -> Jaccard distance + MDS (1 component)
        if matrix_source == "packages":
            mat = np.array(df_computers["_pkg_matrix"].tolist(), dtype=np.float32) if "_pkg_matrix" in df_computers.columns else np.empty((n_samples, 0))
            drift_col = "software_drift_score"
        else:
            mat = np.array(df_computers["_attr_matrix"].tolist(), dtype=np.float32) if "_attr_matrix" in df_computers.columns else np.empty((n_samples, 0))
            drift_col = "jaccard_outlier_score"

        df_computers[drift_col] = 0.0
        lens_bin = None
        dist_matrix = None
        if mat.size > 0 and mat.shape[1] > 0 and mat.sum() > 0:
            try:
                if n_samples >= 3:
                    distances = pdist(mat, metric="jaccard")
                    dist_matrix = squareform(distances)
                    from sklearn.manifold import MDS
                    mds = MDS(n_components=1, dissimilarity="precomputed", random_state=42)
                    lens_bin = mds.fit_transform(dist_matrix)
                    df_computers[drift_col] = dist_matrix.mean(axis=1)
                else:
                    lens_bin = PCA(n_components=1).fit_transform(mat)
            except Exception as ex:
                logger.error(f"Error computing MDS Jaccard for multi_lens '{lens_name}': {ex}")
                lens_bin = None

        # 3. Fuse lenses into a 2D multi-lens projection (Equalized Scale)
        if lens_num is not None and lens_bin is not None:
            lens_num_std = StandardScaler().fit_transform(lens_num)
            lens_bin_std = StandardScaler().fit_transform(lens_bin)
            lens = np.hstack([lens_num_std, lens_bin_std])
        elif lens_num is not None and num_scaled is not None:
            lens = PCA(n_components=min(2, max(1, num_scaled.shape[1]))).fit_transform(num_scaled)
        elif lens_bin is not None and dist_matrix is not None:
            from sklearn.manifold import MDS
            mds2 = MDS(n_components=2, dissimilarity="precomputed", random_state=42)
            lens = mds2.fit_transform(dist_matrix)
        else:
            lens = _pca_fallback()
    else:
        # Default: PCA projection
        lens = _pca_fallback()

    return np.asarray(lens)


class _SkipClusterer(BaseEstimator):
    """Trivial clusterer: every cover element becomes a single node."""

    def fit_predict(self, X, y=None):
        return np.zeros(len(X), dtype=int)


class _FallbackNClusters(BaseEstimator):
    """
    sklearn-compatible wrapper for fixed-n_clusters algorithms (KMeans,
    Agglomerative). Falls back to a single cluster when a cover element has
    fewer points than the requested n_clusters (avoids sklearn errors).
    """

    def __init__(self, factory, n_clusters):
        self.factory = factory
        self.n_clusters = n_clusters

    def fit_predict(self, X, y=None):
        n = len(X)
        if n < self.n_clusters:
            return np.zeros(n, dtype=int)
        return self.factory(self.n_clusters).fit_predict(X)


def _adaptive_eps(cluster_X) -> float:
    """Adaptive DBSCAN eps from the 30th percentile of pairwise distances."""
    n_samples = cluster_X.shape[0]
    try:
        sample_size = min(600, n_samples)
        np.random.seed(42)
        sample_idx = np.random.choice(n_samples, sample_size, replace=False)
        dists = pdist(cluster_X[sample_idx])
        if len(dists) > 0 and np.max(dists) > 0:
            return max(0.5, round(float(np.percentile(dists, 30)), 2))
    except Exception as exc:
        logger.warning(f"Could not compute adaptive eps: {exc}. Using fallback eps=1.5")
    return 1.5


def _build_clusterer(clustering_cfg, cluster_X, n_samples):
    """Build the sklearn-compatible clusterer from the CLUSTERING section.

    Returns (clusterer, description) where description is a short human-readable
    string used for logging.
    """
    clustering_type = clustering_cfg.get("type", "dbscan")
    if clustering_type == "skip":
        return _SkipClusterer(), "skip (one node per cover element)"
    if clustering_type == "kmeans":
        n_clusters = clustering_cfg.get("n_clusters") or 2
        return (
            _FallbackNClusters(
                lambda k: KMeans(n_clusters=k, n_init=10, random_state=42), n_clusters
            ),
            f"kmeans(n_clusters={n_clusters})",
        )
    if clustering_type == "agglomerative":
        n_clusters = clustering_cfg.get("n_clusters") or 2
        return (
            _FallbackNClusters(
                lambda k: AgglomerativeClustering(n_clusters=k), n_clusters
            ),
            f"agglomerative(n_clusters={n_clusters})",
        )
    # dbscan (default)
    eps = clustering_cfg.get("eps")
    if eps is None:
        eps = _adaptive_eps(cluster_X)
    min_samples = clustering_cfg.get("min_samples")
    if min_samples is None:
        min_samples = max(2, min(10, int(np.log10(max(10, n_samples)) * 2)))
    return DBSCAN(eps=eps, min_samples=min_samples), f"dbscan(eps={eps}, min_samples={min_samples})"


def run_mapper(df_computers, feature_matrix, lens_name="health", spec=None, output_dir="/data/tda"):
    """
    Run the Mapper algorithm on the feature matrix.

    Args:
        df_computers: DataFrame with computer metadata
        feature_matrix: numpy array (n_computers × n_features)
        lens_name: name of the TDA lens to apply
        spec: optional validated lens descriptor dict. When None, the lens is
              loaded from the declarative lens store (/data/tda/lenses).
        output_dir: directory to write results

    Returns:
        dict with the Mapper graph in JSON-serializable format
    """
    if feature_matrix.size == 0:
        logger.warning("Empty feature matrix, skipping Mapper")
        return {}

    logger.info(f"Running Mapper with lens '{lens_name}'...")

    # Normalize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(feature_matrix)

    # Resolve the lens descriptor: explicit spec wins, then the declarative store
    if spec is None:
        spec = load_lens(lens_name)
    if spec is None:
        logger.warning(f"Lens '{lens_name}' not found in store; using PCA default")
        spec = {
            "name": lens_name,
            "label": lens_name.capitalize(),
            "description": "",
            "lens": {
                "type": "pca",
                "components": 2,
                "metric_columns": [],
                "matrix_source": None,
            },
            "builtin": False,
        }

    lens = apply_lens_projection(df_computers, feature_matrix, X_scaled, spec)

    # Resolve the COVER section (nullable params fall back to adaptive defaults)
    cover_cfg = spec.get("cover") or {}
    cover_type = cover_cfg.get("type", "cubical")
    if cover_type != "cubical":
        logger.warning(f"Cover type '{cover_type}' is not implemented yet; using cubical cover")

    # Resolve the CLUSTERING section: scaling controls whether the feature
    # matrix is standardized before clustering.
    clustering_cfg = spec.get("clustering") or {}
    scaling = clustering_cfg.get("scaling", True)
    cluster_X = X_scaled if scaling else np.asarray(feature_matrix, dtype=np.float32)

    # Adaptive Mapper parameters calculation
    n_samples = len(df_computers)
    is_2d = lens.ndim > 1 and lens.shape[1] > 1

    # 1. Resolution (n_cubes): config wins, otherwise adaptive.
    #    For 2D lenses, n_cubes is per dimension (total cubes = n_cubes^2).
    n_cubes = resolve_n_cubes(n_samples, is_2d, cover_cfg.get("n_cubes"))

    overlap = cover_cfg.get("overlap")
    if overlap is None:
        overlap = COVER_OVERLAP_DEFAULT

    # 2. Clustering algorithm (SKIP / KMeans / DBSCAN / Agglomerative)
    clusterer, cluster_desc = _build_clusterer(clustering_cfg, cluster_X, n_samples)

    logger.info(
        f"Mapper config for '{lens_name}': n_cubes={n_cubes} (is_2d={is_2d}), "
        f"overlap={overlap}, scaling={scaling}, {cluster_desc}"
    )

    mapper = km.KeplerMapper(verbose=1)

    graph = mapper.map(
        lens,
        cluster_X,
        cover=km.Cover(n_cubes=n_cubes, perc_overlap=overlap),
        clusterer=clusterer,
    )

    # Resolve the per-lens coloring metric (from the lens descriptor or the
    # legacy global /data/tda/config.json "lens_colors")
    color_data, color_function_name, color_kind, color_columns, color_labels = _resolve_lens_color(lens_name, df_computers, spec)

    # Build JSON-serializable output
    draw_cfg = spec.get("draw") or {}
    result = _graph_to_json(
        graph,
        df_computers,
        lens_name,
        color_data=color_data,
        color_label=color_function_name,
        color_kind=color_kind,
        color_columns=color_columns,
        color_labels=color_labels,
        node_label=draw_cfg.get("node_label", "attribute"),
        metric_columns=(spec.get("lens") or {}).get("metric_columns"),
        dataset_metric_columns=(spec.get("dataset") or {}).get("metric_columns"),
        draw=draw_cfg,
    )

    # Helper function to sanitize any nested NaN / Inf / non-compliant float
    def _sanitize_for_json(obj):
        if isinstance(obj, dict):
            return {str(k): _sanitize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [_sanitize_for_json(elem) for elem in obj]
        elif isinstance(obj, float):
            if np.isnan(obj) or np.isinf(obj) or pd.isna(obj):
                return 0.0
            return obj
        elif isinstance(obj, (np.integer, int)):
            return int(obj)
        elif isinstance(obj, (np.floating, float)):
            return 0.0 if (np.isnan(obj) or np.isinf(obj)) else float(obj)
        elif isinstance(obj, np.ndarray):
            return _sanitize_for_json(obj.tolist())
        return obj

    sanitized_result = _sanitize_for_json(result)

    # Save to file (self-contained lens folder: <output_dir>/lenses/<name>/mapper.json)
    output_file = resolve_lens_output_path(output_dir, lens_name, "json")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(sanitized_result, f, indent=2, allow_nan=False, default=str)

    logger.info(f"Mapper result saved to {output_file}")

    # Also generate the KeplerMapper HTML visualization if nodes exist
    if graph and graph.get("nodes") and len(graph["nodes"]) > 0:
        html_file = resolve_lens_output_path(output_dir, lens_name, "html")

        # Generate custom tooltips with HTML links to the computer detail pages in Migasfree
        fqdn = os.getenv("FQDN", "localhost")
        custom_tooltips = []
        for _, r in df_computers.iterrows():
            comp_id = r.get("computer_id", "")
            comp_name = r.get("computer_name", "")
            link = f'<a href="https://{fqdn}/computers/results/{comp_id}" target="_blank" style="color: #0d6efd; text-decoration: underline; font-weight: bold;">{comp_name}</a>'
            custom_tooltips.append(link)

        mapper.visualize(
            graph,
            path_html=html_file,
            title=f"Migasfree TDA - {lens_name.capitalize()} Lens",
            color_values=color_data,
            color_function_name=color_function_name,
            custom_tooltips=np.array(custom_tooltips),
        )
        logger.info(f"Mapper visualization saved to {html_file}")
    else:
        logger.warning(f"Mapper graph for lens '{lens_name}' has 0 nodes; skipping HTML visualization.")

    return result


def _graph_to_json(graph, df_computers, lens_name, color_data=None, color_label=None, color_kind="continuous", color_columns=None, color_labels=None, node_label="attribute", metric_columns=None, dataset_metric_columns=None, draw=None):
    """Convert the KeplerMapper graph to a JSON-serializable dict."""
    nodes = []
    edges = []

    def _safe_float(val, default=0.0):
        if val is None or pd.isna(val) or np.isnan(val) or np.isinf(val):
            return default
        return float(val)

    def _safe_int(val, default=0):
        if val is None or pd.isna(val) or np.isnan(val) or np.isinf(val):
            return default
        return int(val)

    def _collect_attr_ids(row):
        ids = []
        for col in ("attribute_ids", "tag_ids"):
            val = row.get(col)
            if isinstance(val, (list, tuple, np.ndarray)):
                for v in val:
                    if v is not None and not (isinstance(v, float) and np.isnan(v)):
                        try:
                            ids.append(int(v))
                        except (ValueError, TypeError):
                            continue
            elif val is not None and not pd.isna(val):
                try:
                    ids.append(int(val))
                except (ValueError, TypeError):
                    continue
        return ids

    # Fleet-wide attribute prevalence, used to highlight which attributes
    # are characteristic of each node ("reason for grouping")
    attr_names = getattr(df_computers, "attrs", {}).get("attr_names", {})
    # Restrict the reason-for-grouping to the attributes included in the
    # TDA computation (formula prefixes selected in the settings)
    matrix_attr_ids = getattr(df_computers, "attrs", {}).get("matrix_attr_ids")
    fleet_counts = Counter()
    for _, row in df_computers.iterrows():
        for aid in _collect_attr_ids(row):
            fleet_counts[aid] += 1
    fleet_total = max(len(df_computers), 1)

    node_map = {}  # kepler node_id -> sequential index

    for idx, (node_id, member_indices) in enumerate(graph["nodes"].items()):
        node_map[node_id] = idx
        members = member_indices

        # Aggregate metadata for members
        member_data = df_computers.iloc[members]

        # Most shared / distinctive attributes within the node ("reason for grouping")
        node_counts = Counter()
        for _, row in member_data.iterrows():
            for aid in _collect_attr_ids(row):
                node_counts[aid] += 1
        node_size = max(len(members), 1)
        top_attributes = []
        for aid, cnt in node_counts.most_common(20):
            if matrix_attr_ids is not None and aid not in matrix_attr_ids:
                continue
            pct = cnt / node_size
            global_pct = fleet_counts.get(aid, 0) / fleet_total
            # Skip attributes present in (almost) the whole fleet: they are
            # common to every group and do not explain why a node is grouped.
            if global_pct >= 0.95:
                continue
            lift = (pct + 0.01) / (global_pct + 0.01)
            top_attributes.append({
                "name": attr_names.get(aid, f"attr-{aid}"),
                "count": int(cnt),
                "pct": round(pct * 100, 1),
                "lift": round(lift, 2),
            })
        top_attributes.sort(key=lambda a: a["lift"], reverse=True)
        top_attributes = top_attributes[:8]

        node_cids = []
        node_cnames = []
        for _, row in member_data.iterrows():
            cid = row.get("computer_id")
            if pd.notnull(cid):
                node_cids.append(int(cid))
                cname = row.get("computer_name")
                node_cnames.append(str(cname) if pd.notnull(cname) and str(cname).strip() else f"#{int(cid)}")

        node_info = {
            "id": idx,
            "kepler_id": node_id,
            "size": len(members),
            "top_attributes": top_attributes,
            "computer_ids": node_cids,
            "computer_names": node_cnames,
            "projects": [
                {
                    "id": int(p_id) if pd.notnull(p_id) and str(p_id).isdigit() else (str(p_id) if pd.notnull(p_id) else "None"),
                    "name": str(p_name) if pd.notnull(p_name) else f"Project {p_id}",
                    "count": int(count)
                }
                for (p_id, p_name), count in member_data.groupby(
                    ["project_id", "project_name"], dropna=False
                ).size().items()
            ] if "project_name" in member_data.columns else [
                {"id": p_id if pd.notnull(p_id) else "None", "name": f"Project {p_id}", "count": int(count)}
                for p_id, count in member_data["project_id"].value_counts(dropna=False).items()
            ],
            "statuses": {str(k): int(v) for k, v in member_data["status"].value_counts().items() if pd.notnull(k)},
            "machine_types": {str(k): int(v) for k, v in member_data["machine"].value_counts().items() if pd.notnull(k)}
            if "machine" in member_data.columns else {},
            "avg_machine_type": _safe_float(member_data["machine_type"].mean())
            if "machine_type" in member_data.columns else 0.0,
            "avg_errors": _safe_float(member_data["error_count"].mean())
            if "error_count" in member_data.columns else 0.0,
            "avg_faults": _safe_float(member_data["fault_count"].mean())
            if "fault_count" in member_data.columns else 0.0,
            "avg_sync_duration": _safe_float(member_data["avg_sync_duration_secs"].mean())
            if "avg_sync_duration_secs" in member_data.columns else 0.0,
            "avg_sync_count": _safe_float(member_data["sync_count"].mean())
            if "sync_count" in member_data.columns else 0.0,
            "avg_pms_failures": _safe_float(member_data["pms_failures"].mean())
            if "pms_failures" in member_data.columns else 0.0,
            "avg_ram_gb": _safe_float(member_data["ram_gb"].mean())
            if "ram_gb" in member_data.columns else 0.0,
            "avg_disk_gb": _safe_float(member_data["disk_gb"].mean())
            if "disk_gb" in member_data.columns else 0.0,
            "avg_computer_age_days": _safe_float(member_data["computer_age_days"].mean())
            if "computer_age_days" in member_data.columns else 0.0,
            "avg_days_since_last_sync": _safe_float(member_data["days_since_last_sync"].mean())
            if "days_since_last_sync" in member_data.columns else 0.0,
            "avg_days_since_migration": _safe_float(member_data["days_since_last_migration"].mean())
            if "days_since_last_migration" in member_data.columns else 0.0,
            "cpu_models": [str(c) for c in member_data["cpu_product"].unique().tolist() if pd.notnull(c) and str(c) != 'None']
            if "cpu_product" in member_data.columns else [],
            "gpus": [str(g) for g in member_data["gpus"].unique().tolist() if pd.notnull(g) and str(g) != 'None']
            if "gpus" in member_data.columns else [],
            "avg_packages": _safe_float(member_data["total_packages"].mean())
            if "total_packages" in member_data.columns else 0.0,
            "avg_migrations": _safe_float(member_data["migration_count"].mean())
            if "migration_count" in member_data.columns else 0.0,
            "migrated_count": _safe_int((member_data["migration_count"] > 0).sum())
            if "migration_count" in member_data.columns else 0,
        }
        if color_data is not None:
            node_color_values = np.asarray(color_data, dtype=np.float64)[members]
            node_info["color_value"] = _safe_float(float(node_color_values.mean()))
            if color_kind == "categorical":
                if color_labels is not None:
                    # Readable per-value categories (e.g. prefix colors):
                    # "CTX-aula": 3, "CTX-office": 1 ...
                    category_counts = {}
                    for label in np.asarray(color_labels)[members].tolist():
                        if label in (None, "", "nan"):
                            continue
                        category_counts[str(label)] = category_counts.get(str(label), 0) + 1
                else:
                    category_counts = {}
                    for v in node_color_values:
                        key = str(int(v)) if float(v).is_integer() else str(round(float(v), 4))
                        category_counts[key] = category_counts.get(key, 0) + 1
                if category_counts:
                    node_info["color_categories"] = dict(
                        sorted(category_counts.items(), key=lambda kv: kv[1], reverse=True)
                    )
        nodes.append(node_info)

    # Node computer id sets, used to explain why each edge exists
    node_computer_ids = [set(n["computer_ids"]) for n in nodes]
    node_name_maps = [
        dict(zip(n["computer_ids"], n["computer_names"])) for n in nodes
    ]

    for edge in graph["links"].items():
        src_kepler_id = edge[0]
        for target_kepler_id in edge[1]:
            if src_kepler_id in node_map and target_kepler_id in node_map:
                src = node_map[src_kepler_id]
                tgt = node_map[target_kepler_id]
                shared = sorted(node_computer_ids[src] & node_computer_ids[tgt])
                edges.append({
                    "source": src,
                    "target": tgt,
                    "shared_count": len(shared),
                    "shared_computer_ids": [int(cid) for cid in shared],
                    "shared_computer_names": [node_name_maps[src].get(int(cid), f"#{cid}") for cid in shared],
                })

    prefix_to_name = getattr(df_computers, "attrs", {}).get("prefix_to_name", {})
    metadata = {
        "lens": lens_name,
        "node_label": node_label if node_label in NODE_LABELS else "attribute",
        "metric_columns": [str(c) for c in (metric_columns or [])],
        "dataset_metric_columns": [str(c) for c in (dataset_metric_columns or [])],
        "prefix_names": prefix_to_name,
        "generated_at": datetime.utcnow().isoformat(),
        "total_computers": len(df_computers),
        "total_nodes": len(nodes),
        "total_edges": len(edges),
    }
    if isinstance(draw, dict):
        metadata["draw"] = {
            "dimensions": draw.get("dimensions", 3),
            "iterations": draw.get("iterations", 100),
            "seed": draw.get("seed"),
        }
    if color_label is not None:
        metadata["color"] = {
            "label": str(color_label),
            "kind": color_kind if color_kind in COLOR_KINDS else "continuous",
            "columns": [str(c) for c in (color_columns or [])],
        }

    return {
        "metadata": metadata,
        "nodes": nodes,
        "edges": edges,
    }

