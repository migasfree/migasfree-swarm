"""
Lens Store: declarative, user-defined lenses for the TDA service.

Each lens lives in its own self-contained folder under /data/tda/lenses/:

    /data/tda/lenses/<name>/
        config.json     ← lens descriptor (configuration)
        mapper.json     ← generated Mapper graph (JSON)
        mapper.html     ← KeplerMapper diagnostic visualization

The six built-in lenses are seeded on first start and can be edited
(label, description, metric columns, coloring, filters) but never
deleted or renamed.

Lens descriptor schema (organized following the Mapper pipeline flow):

    {
      "name": "my_lens",            # unique slug (^[a-z0-9][a-z0-9_-]{1,63}$)
      "label": "My Lens",           # display name
      "description": "...",         # optional explanation shown in the dashboard
      "builtin": true|false,        # built-in lenses cannot be deleted/renamed

      # ── DATASET: scope & dimension selections ──
      "dataset": {
          "scope_ids": [...],           # restrict to these scopes ([] = no filter)
          "formula_prefix_ids": [...],  # attribute types to include in TDA computation
          "metric_columns": [...],      # numeric metric columns to include in the
                                        #   feature matrix (missing = all metrics)
      },

      # ── LENS: projection / filter function ──
      "lens": {
          "type": "identity" | "pca" | "mds_jaccard",
          "components": 2,          # 1 | 2 (PCA components; identity derives it
                                    #   from the number of metric_columns)
          "metric_columns": [...],  # identity: 1–2 raw metric columns
          "matrix_source": "attributes" | "packages"   # only for mds_jaccard
      },

      # ── COVER: overlapping intervals/cubes over the lens ──
      "cover": {
          "type": "cubical",        # cubical | ball | knn  (ball/knn deferred)
          "n_cubes": null,          # cubical: null = adaptive
          "overlap": null,          # cubical: null = 0.35 default
          "radius": null,           # ball (deferred)
          "n_neighbors": null       # knn (deferred)
      },

      # ── CLUSTERING: partition points within each cover element ──
      "clustering": {
          "scaling": true,          # standardize the feature matrix before clustering
          "type": "dbscan",         # skip | kmeans | dbscan | agglomerative
          "n_clusters": null,       # kmeans/agglomerative
          "eps": null,              # dbscan: null = adaptive
          "min_samples": null       # dbscan: null = adaptive
      },

      # ── DRAW: graph layout & node appearance ──
      "draw": {
          "dimensions": 2,          # 2 | 3 (graph layout dimensionality)
          "iterations": 100,        # force-layout iterations
          "seed": null,             # layout seed (null = random)
          "color": {                # metric used to color the Mapper nodes
              "columns": [...],
              "label": "...",
              "kind": "continuous" | "categorical"
          },
          "node_label": "attribute" | "metric"   # text shown under each node
      }
    }

    UMAP will be added next.

    For backward compatibility the legacy flat keys (formula_prefix_ids,
    scope_ids for DATASET; projection, metric_columns, matrix_source for
    LENS) are still accepted and normalized into their nested sections.
"""

import os
import re
import json
import shutil
import logging
from typing import Optional

logger = logging.getLogger("migasfree-tda")

TDA_DIR = os.getenv("TDA_DIR", "/data/tda")
LENSES_DIR = os.path.join(TDA_DIR, "lenses")
TDA_CONFIG_PATH = os.path.join(TDA_DIR, "config.json")

LENS_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_\-]{1,63}$")

LENS_TYPES = ("identity", "pca", "mds_jaccard", "multi_lens")
MATRIX_SOURCES = ("attributes", "packages")
COLOR_KINDS = ("continuous", "categorical")
NODE_LABELS = ("attribute", "metric")
COVER_TYPES = ("cubical", "ball", "knn")
COVER_OVERLAP_DEFAULT = 0.35
CLUSTERING_TYPES = ("skip", "kmeans", "dbscan", "agglomerative")

# Legacy projection names mapped to the new LENS types.
LEGACY_PROJECTION_MAP = {
    "pca": "pca",
    "mds_jaccard": "mds_jaccard",
    "multi_lens": "multi_lens",
    "hybrid": "multi_lens",
    "metric_pair": "identity",
    "single_metric": "identity",
    "identity": "identity",
}

LENS_TYPE_LABELS = {
    "identity": "Identity",
    "pca": "PCA",
    "mds_jaccard": "Jaccard + MDS",
    "multi_lens": "Multi-Lens (PCA + Jaccard)",
}

FORMULA_PREFIX_DEFAULT = [3, 5]
DEFAULT_METRICS_INTERVAL_DAYS = 365

# Numeric metric columns that can be included in the DATASET feature matrix.
# Order is preserved when building the matrix (see tda_engine.build_feature_matrix).
DATASET_METRICS = (
    "error_count",
    "fault_count",
    "sync_count",
    "avg_sync_duration_secs",
    "pms_failures",
    "ram_gb",
    "disk_gb",
    "machine_type",
    "computer_age_days",
    "days_since_last_sync",
    "total_packages",
    "migration_count",
    "days_since_last_migration",
)

LENS_COLOR_DEFAULTS = {
    "health": {"columns": ["error_count"], "label": "Error Count", "kind": "continuous"},
    "obsolescence": {"columns": ["ram_gb"], "label": "RAM (GB)", "kind": "continuous"},
    "sync": {"columns": ["avg_sync_duration_secs"], "label": "Avg Sync Duration (secs)", "kind": "continuous"},
    "software": {"columns": ["total_packages"], "label": "Total Installed Packages", "kind": "continuous"},
    "migration": {"columns": ["migration_count"], "label": "Migrations Count", "kind": "continuous"},
    "diversity": {"columns": ["jaccard_outlier_score"], "label": "Configuration Outlier Score (Mean Jaccard Distance)", "kind": "continuous"},
}

DEFAULT_LENS_COLOR = {"columns": ["error_count"], "label": "Error Count", "kind": "continuous"}

# Legacy layout (pre-folder): /data/tda/mapper_<name>.{json,html}
LEGACY_PREFIX = "mapper_"

BUILTIN_LENSES = [
    {
        "name": "health",
        "label": "Health",
        "description": "Error & fault rate. Groups computers by operational incidents in the last 30 days.",
        "projection": "metric_pair",
        "metric_columns": ["error_count", "fault_count"],
        "matrix_source": None,
        "builtin": True,
    },
    {
        "name": "obsolescence",
        "label": "Obsolescence",
        "description": "Hardware capacity & profiles (PCA over the full feature space).",
        "projection": "pca",
        "metric_columns": [],
        "matrix_source": None,
        "builtin": True,
    },
    {
        "name": "software",
        "label": "Software",
        "description": "Package drift & archetypes (Jaccard distance over installed packages + MDS).",
        "projection": "mds_jaccard",
        "metric_columns": [],
        "matrix_source": "packages",
        "builtin": True,
    },
    {
        "name": "migration",
        "label": "Migration",
        "description": "Trajectories & bottlenecks (migration count vs days since last migration).",
        "projection": "metric_pair",
        "metric_columns": ["migration_count", "days_since_last_migration"],
        "matrix_source": None,
        "builtin": True,
    },
    {
        "name": "sync",
        "label": "Sync",
        "description": "Sync speed & PMS failures.",
        "projection": "metric_pair",
        "metric_columns": ["avg_sync_duration_secs", "pms_failures"],
        "matrix_source": None,
        "builtin": True,
    },
    {
        "name": "diversity",
        "label": "Diversity",
        "description": "Config divergence (Jaccard distance over attributes/tags + MDS).",
        "projection": "mds_jaccard",
        "metric_columns": [],
        "matrix_source": "attributes",
        "builtin": True,
    },
]


def lens_dir(name: str) -> str:
    """Absolute path of the self-contained folder of a lens."""
    return os.path.join(LENSES_DIR, name)


def _lens_path(name: str) -> str:
    """Absolute path of the lens descriptor file."""
    return os.path.join(lens_dir(name), "config.json")


def lens_output_path(name: str, ext: str = "json") -> str:
    """Absolute path of a generated output (mapper.json / mapper.html)."""
    return os.path.join(lens_dir(name), f"mapper.{ext}")


def legacy_output_path(name: str, ext: str = "json") -> str:
    """Legacy path /data/tda/mapper_<name>.<ext> (pre-folder layout)."""
    return os.path.join(TDA_DIR, f"{LEGACY_PREFIX}{name}.{ext}")


def resolve_lens_output_path(output_dir: str, name: str, ext: str = "json") -> str:
    """Resolve where a lens output must be written, given a base data dir."""
    return os.path.join(output_dir, "lenses", name, f"mapper.{ext}")


def has_lens_output(name: str, ext: str = "json") -> bool:
    """True when the lens has a generated output in its folder."""
    return os.path.isfile(lens_output_path(name, ext))


def migrate_legacy_outputs() -> None:
    """
    Move legacy /data/tda/mapper_<name>.{json,html} files into their lens
    folders (/data/tda/lenses/<name>/mapper.<ext>). Idempotent.
    """
    if not os.path.isdir(TDA_DIR):
        return
    try:
        for filename in os.listdir(TDA_DIR):
            if not filename.startswith(LEGACY_PREFIX):
                continue
            if not filename.endswith((".json", ".html")):
                continue
            ext = "html" if filename.endswith(".html") else "json"
            name = filename[len(LEGACY_PREFIX):-len(f".{ext}")]
            if not name:
                continue
            dest = lens_output_path(name, ext)
            if os.path.isfile(dest):
                continue
            try:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                os.rename(os.path.join(TDA_DIR, filename), dest)
                logger.info(f"Migrated legacy output {filename} -> {dest}")
            except Exception as exc:
                logger.warning(f"Could not migrate legacy output {filename}: {exc}")
    except Exception as exc:
        logger.warning(f"Could not scan legacy outputs in {TDA_DIR}: {exc}")


def _positive_ids(value) -> list:
    """Coerce a value into a list of positive integers (empty list allowed)."""
    if not isinstance(value, (list, tuple)):
        return []
    return [int(i) for i in value if str(i).strip().isdigit() and int(i) > 0]


def _normalize_metric_columns(value) -> list:
    """
    Normalize the DATASET metric selection.

    `None` (or a missing key) means "all metrics" (backward compatible with
    the previous always-all behavior). A list selects the named metrics,
    keeping only known names and preserving their order; an empty list means
    "no metrics".
    """
    if value is None:
        return list(DATASET_METRICS)
    if not isinstance(value, (list, tuple)):
        value = [value]
    known = set(DATASET_METRICS)
    seen = set()
    result = []
    for entry in value:
        name = str(entry).strip()
        if name in known and name not in seen:
            result.append(name)
            seen.add(name)
    return result


def _normalize_interval_days(value) -> int:
    """Coerce a value into a positive integer representing days."""
    try:
        val = int(value)
        if val > 0:
            return val
    except (ValueError, TypeError):
        pass
    return DEFAULT_METRICS_INTERVAL_DAYS


def _normalize_dataset(data: dict) -> dict:
    """
    Normalize the DATASET section (scope & dimension selections).

    Accepts both the nested `dataset` object and the legacy flat keys
    (formula_prefix_ids / scope_ids). A nested value wins over
    its flat counterpart; the flat key fills any gap. Missing entries default
    to an empty list (metrics default to "all", interval defaults to 365).
    """
    nested = data.get("dataset")
    if not isinstance(nested, dict):
        nested = {}

    def _pick(nested_key, flat_key):
        value = nested.get(nested_key)
        if value is None:
            value = data.get(flat_key)
        return value

    return {
        "formula_prefix_ids": _positive_ids(_pick("formula_prefix_ids", "formula_prefix_ids")),
        "scope_ids": _positive_ids(_pick("scope_ids", "scope_ids")),
        "metric_columns": _normalize_metric_columns(nested.get("metric_columns")),
        "metrics_interval_days": _normalize_interval_days(
            _pick("metrics_interval_days", "metrics_interval_days")
        ),
    }


def _normalize_color(value) -> dict:
    """Validate/normalize the per-lens coloring descriptor."""
    if not isinstance(value, dict):
        return dict(DEFAULT_LENS_COLOR)
    columns = value.get("columns") or []
    if not isinstance(columns, (list, tuple)):
        columns = [columns]
    columns = [str(c).strip() for c in columns if str(c).strip()]
    if not columns:
        return dict(DEFAULT_LENS_COLOR)
    kind = str(value.get("kind") or "")
    if kind not in COLOR_KINDS:
        kind = "categorical" if "project_encoded" in columns else "continuous"
    return {
        "columns": columns,
        "label": str(value.get("label") or columns[0]),
        "kind": kind,
    }


def _normalize_lens(data: dict) -> dict:
    """
    Normalize the LENS section (projection / filter function).

    Accepts both the nested `lens` object and the legacy flat keys
    (projection / metric_columns / matrix_source). Legacy projection names are
    mapped to the new types (metric_pair/single_metric → identity). Unknown
    types fall back to "pca" (matching the engine's previous fallback).
    """
    nested = data.get("lens") if isinstance(data.get("lens"), dict) else {}

    raw_type = nested.get("type") or data.get("projection") or "pca"
    lens_type = LEGACY_PROJECTION_MAP.get(str(raw_type).strip().lower(), "pca")

    metric_columns = nested.get("metric_columns")
    if metric_columns is None:
        metric_columns = data.get("metric_columns")
    if not isinstance(metric_columns, (list, tuple)):
        metric_columns = [metric_columns] if metric_columns else []
    metric_columns = [str(c).strip() for c in metric_columns if str(c).strip()]

    if lens_type == "identity":
        metric_columns = metric_columns[:2]
        components = len(metric_columns)
    else:
        metric_columns = []
        components = 2

    matrix_source = nested.get("matrix_source")
    if matrix_source is None:
        matrix_source = data.get("matrix_source")
    if lens_type not in ("mds_jaccard", "multi_lens") or matrix_source not in MATRIX_SOURCES:
        matrix_source = "attributes" if lens_type == "multi_lens" else None

    if lens_type in ("pca", "multi_lens"):
        raw_components = nested.get("components", 2)
        try:
            components = int(raw_components)
        except (ValueError, TypeError):
            components = 2
        if components not in (1, 2):
            components = 2

    return {
        "type": lens_type,
        "components": components,
        "metric_columns": metric_columns,
        "matrix_source": matrix_source,
    }


def _nullable_int(value):
    """Coerce to int or None (None on empty/invalid)."""
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def _nullable_float(value):
    """Coerce to float or None (None on empty/invalid)."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _normalize_cover(data: dict) -> dict:
    """
    Normalize the COVER section.

    `n_cubes`/`overlap`/`radius`/`n_neighbors` are nullable: None means the
    engine falls back to its adaptive/default values. Only the `cubical` cover
    is implemented so far; `ball` and `knn` are kept in the schema for later.
    """
    nested = data.get("cover") if isinstance(data.get("cover"), dict) else {}

    cover_type = str(nested.get("type") or "cubical").strip()
    if cover_type not in COVER_TYPES:
        cover_type = "cubical"

    n_cubes = _nullable_int(nested.get("n_cubes"))
    if n_cubes is not None and n_cubes <= 0:
        n_cubes = None

    overlap = _nullable_float(nested.get("overlap"))
    if overlap is not None and not (0.0 <= overlap < 1.0):
        overlap = None

    radius = _nullable_float(nested.get("radius"))

    n_neighbors = _nullable_int(nested.get("n_neighbors"))
    if n_neighbors is not None and n_neighbors <= 0:
        n_neighbors = None

    return {
        "type": cover_type,
        "n_cubes": n_cubes,
        "overlap": overlap,
        "radius": radius,
        "n_neighbors": n_neighbors,
    }


def _normalize_clustering(data: dict) -> dict:
    """
    Normalize the CLUSTERING section.

    `n_clusters`/`eps`/`min_samples` are nullable: None means the engine uses
    its adaptive/default values (DBSCAN eps/min_samples are adaptive).
    """
    nested = data.get("clustering") if isinstance(data.get("clustering"), dict) else {}

    clustering_type = str(nested.get("type") or "dbscan").strip()
    if clustering_type not in CLUSTERING_TYPES:
        clustering_type = "dbscan"

    scaling = nested.get("scaling", True)
    if not isinstance(scaling, bool):
        scaling = True

    n_clusters = _nullable_int(nested.get("n_clusters"))
    if n_clusters is not None and n_clusters < 2:
        n_clusters = None

    eps = _nullable_float(nested.get("eps"))
    if eps is not None and eps <= 0:
        eps = None

    min_samples = _nullable_int(nested.get("min_samples"))
    if min_samples is not None and min_samples < 1:
        min_samples = None

    return {
        "scaling": scaling,
        "type": clustering_type,
        "n_clusters": n_clusters,
        "eps": eps,
        "min_samples": min_samples,
    }


def _normalize_draw(data: dict) -> dict:
    """
    Normalize the DRAW section (graph layout & node appearance).

    Accepts both the nested `draw` object and the legacy flat `color` /
    `node_label` keys. Nested values win; flat values fill any gap.
    """
    nested = data.get("draw") if isinstance(data.get("draw"), dict) else {}

    dimensions = nested.get("dimensions", 3)
    try:
        dimensions = int(dimensions)
    except (ValueError, TypeError):
        dimensions = 3
    if dimensions not in (2, 3):
        dimensions = 3

    iterations = _nullable_int(nested.get("iterations"))
    if iterations is None or iterations <= 0:
        iterations = 100

    seed = _nullable_int(nested.get("seed"))

    color_value = nested.get("color")
    if color_value is None:
        color_value = data.get("color")
    color = _normalize_color(color_value)

    node_label = nested.get("node_label")
    if node_label is None:
        node_label = data.get("node_label")
    node_label = str(node_label or "attribute").strip()
    if node_label not in NODE_LABELS:
        node_label = "attribute"

    return {
        "dimensions": dimensions,
        "iterations": iterations,
        "seed": seed,
        "color": color,
        "node_label": node_label,
    }


def validate_lens(data: dict, current_name: Optional[str] = None) -> dict:
    """
    Validate and normalize a lens descriptor.

    Args:
        data: raw descriptor dict (from API or disk)
        current_name: existing name when updating (used to detect renames)

    Returns:
        normalized descriptor dict

    Raises:
        ValueError: when the descriptor is invalid
    """
    if not isinstance(data, dict):
        raise ValueError("Lens descriptor must be an object")

    name = str(data.get("name") or "").strip().lower()
    if not LENS_NAME_RE.match(name):
        raise ValueError(
            "name must match ^[a-z0-9][a-z0-9_-]{1,63}$ (lowercase letters, digits, dashes)"
        )
    if current_name and name != current_name:
        raise ValueError("lens name cannot be changed")

    label = str(data.get("label") or "").strip()
    if not label:
        raise ValueError("label is required")

    lens = _normalize_lens(data)
    if lens["type"] == "identity" and not (1 <= len(lens["metric_columns"]) <= 2):
        raise ValueError("lens type 'identity' requires 1 or 2 metric_columns")
    if lens["type"] == "mds_jaccard" and lens["matrix_source"] is None:
        raise ValueError(
            f"lens type 'mds_jaccard' requires matrix_source in: {', '.join(MATRIX_SOURCES)}"
        )

    return {
        "name": name,
        "label": label,
        "description": str(data.get("description") or "").strip(),
        "dataset": _normalize_dataset(data),
        "lens": lens,
        "cover": _normalize_cover(data),
        "clustering": _normalize_clustering(data),
        "draw": _normalize_draw(data),
        "scheduled": bool(data.get("scheduled", True)),
        "builtin": bool(data.get("builtin", False)),
    }


def migrate_lens_descriptor_files() -> None:
    """
    Rename old lens descriptor files (lens.json) to config.json inside each
    lens folder. Idempotent; supports the pre-config.json layout.
    """
    if not os.path.isdir(LENSES_DIR):
        return
    for entry in os.listdir(LENSES_DIR):
        old_path = os.path.join(LENSES_DIR, entry, "lens.json")
        new_path = os.path.join(LENSES_DIR, entry, "config.json")
        if os.path.isfile(old_path) and not os.path.isfile(new_path):
            try:
                os.rename(old_path, new_path)
                logger.info(f"Migrated lens descriptor {old_path} -> {new_path}")
            except Exception as exc:
                logger.warning(f"Could not migrate lens descriptor {old_path}: {exc}")


def _global_config() -> dict:
    """Read the legacy global config (/data/tda/config.json), best effort."""
    try:
        if os.path.isfile(TDA_CONFIG_PATH):
            with open(TDA_CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            return cfg if isinstance(cfg, dict) else {}
    except Exception as exc:
        logger.warning(f"Could not read global TDA config: {exc}")
    return {}


def _migrate_builtin_descriptor(spec: dict, global_cfg: dict) -> bool:
    """
    Patch a built-in lens descriptor with the per-lens keys (color, prefixes,
    scopes) when they are missing (upgrade from pre-per-lens layouts).
    Returns True when the descriptor was modified.
    """
    name = spec["name"]
    changed = False
    if "color" not in spec or not isinstance(spec.get("color"), dict):
        global_colors = global_cfg.get("lens_colors") or {}
        spec["color"] = _normalize_color(
            global_colors.get(name) or LENS_COLOR_DEFAULTS.get(name) or DEFAULT_LENS_COLOR
        )
        changed = True
    if "node_label" not in spec or spec.get("node_label") not in NODE_LABELS:
        spec["node_label"] = "attribute"
        changed = True
    # Migrate the legacy flat dataset keys into a nested `dataset` section,
    # and backfill any missing dataset fields (e.g. metric_columns).
    nested = spec.get("dataset") if isinstance(spec.get("dataset"), dict) else {}
    global_prefixes = _positive_ids(global_cfg.get("formula_prefix_ids"))
    normalized = _normalize_dataset(
        {
            "dataset": nested,
            "formula_prefix_ids": nested.get(
                "formula_prefix_ids",
                spec.get("formula_prefix_ids", global_prefixes or list(FORMULA_PREFIX_DEFAULT)),
            ),
            "scope_ids": nested.get("scope_ids", spec.get("scope_ids", [])),
        }
    )
    if spec.get("dataset") != normalized:
        spec["dataset"] = normalized
        changed = True
    for key in ("formula_prefix_ids", "scope_ids", "metrics_interval_days"):
        spec.pop(key, None)

    # Migrate the legacy flat projection keys into a nested `lens` section.
    normalized_lens = _normalize_lens(spec)
    if spec.get("lens") != normalized_lens:
        spec["lens"] = normalized_lens
        changed = True
    for key in ("projection", "metric_columns", "matrix_source"):
        spec.pop(key, None)

    # Ensure the `cover` section is present and normalized (defaults adaptive).
    normalized_cover = _normalize_cover(spec)
    if spec.get("cover") != normalized_cover:
        spec["cover"] = normalized_cover
        changed = True

    # Ensure the `clustering` section is present and normalized.
    normalized_clustering = _normalize_clustering(spec)
    if spec.get("clustering") != normalized_clustering:
        spec["clustering"] = normalized_clustering
        changed = True

    # Migrate legacy flat color/node_label into a nested `draw` section.
    normalized_draw = _normalize_draw(spec)
    if spec.get("draw") != normalized_draw:
        spec["draw"] = normalized_draw
        changed = True
    for key in ("color", "node_label"):
        spec.pop(key, None)
    return changed


def seed_builtin_lenses() -> None:
    """Ensure the built-in lenses exist on disk (idempotent)."""
    os.makedirs(LENSES_DIR, exist_ok=True)
    migrate_lens_descriptor_files()
    global_cfg = _global_config()
    for spec in BUILTIN_LENSES:
        path = _lens_path(spec["name"])
        if not os.path.isfile(path):
            descriptor = dict(spec)
            _migrate_builtin_descriptor(descriptor, global_cfg)
            try:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(descriptor, f, indent=2)
                logger.info(f"Seeded built-in lens '{spec['name']}' -> {path}")
            except Exception as exc:
                logger.warning(f"Could not seed lens '{spec['name']}': {exc}")
        else:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                if _migrate_builtin_descriptor(existing, global_cfg):
                    with open(path, "w", encoding="utf-8") as f:
                        json.dump(existing, f, indent=2)
                    logger.debug(f"Migrated built-in lens descriptor '{spec['name']}' -> {path}")
            except Exception as exc:
                logger.warning(f"Could not migrate built-in lens descriptor '{spec['name']}': {exc}")
    migrate_legacy_outputs()


def list_lenses() -> list:
    """Return lens names ordered: built-ins first (seed order), then custom alphabetically."""
    seed_builtin_lenses()
    names = []
    try:
        for entry in sorted(os.listdir(LENSES_DIR)):
            entry_path = os.path.join(LENSES_DIR, entry)
            if os.path.isdir(entry_path) and os.path.isfile(os.path.join(entry_path, "config.json")):
                names.append(entry)
    except FileNotFoundError:
        return []
    builtin_names = [s["name"] for s in BUILTIN_LENSES]
    return [n for n in builtin_names if n in names] + [
        n for n in names if n not in builtin_names
    ]


def load_lens(name: str) -> Optional[dict]:
    """Load a single lens descriptor, or None when it does not exist."""
    path = _lens_path(name)
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return validate_lens(data, current_name=name)
    except Exception as exc:
        logger.warning(f"Could not read lens '{name}': {exc}")
        return None


def load_all_lenses() -> list:
    """Load every lens descriptor in the store (built-ins are always present)."""
    seed_builtin_lenses()
    lenses = []
    for name in list_lenses():
        spec = load_lens(name)
        if spec:
            lenses.append(spec)
    return lenses


def save_lens(spec: dict) -> dict:
    """Persist a validated lens descriptor. Returns the normalized spec."""
    name = spec["name"]
    path = _lens_path(name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2)
    logger.info(f"Lens '{name}' saved")
    return spec


def delete_lens(name: str) -> None:
    """Delete a lens: its folder and any legacy generated outputs."""
    spec = load_lens(name)
    if spec is None:
        raise ValueError(f"Lens '{name}' not found")
    if os.path.isdir(lens_dir(name)):
        shutil.rmtree(lens_dir(name), ignore_errors=True)
    for ext in ("json", "html"):
        legacy = legacy_output_path(name, ext)
        try:
            os.remove(legacy)
        except FileNotFoundError:
            pass
    logger.info(f"Lens '{name}' deleted")
