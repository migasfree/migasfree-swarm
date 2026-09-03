"""
TDA Service Configuration & Constants
"""
import os
import logging

logger = logging.getLogger("migasfree-tda")

TDA_DIR = "/data/tda"
TDA_CONFIG_PATH = os.path.join(TDA_DIR, "config.json")
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CORE_URL = os.getenv("CORE_URL", "http://core:8080")
CORE_LOGIN_URL = f"{CORE_URL}/rest-auth/login/"
CORE_USER_URL = f"{CORE_URL}/rest-auth/user/"

FORMULA_PREFIX_DEFAULT = []

LENS_COLORS_DEFAULT = {
    "health": {"columns": ["error_count"], "label": "Error Count", "kind": "continuous"},
    "obsolescence": {"columns": ["ram_gb"], "label": "RAM (GB)", "kind": "continuous"},
    "sync": {"columns": ["avg_sync_duration_secs"], "label": "Avg Sync Duration (secs)", "kind": "continuous"},
    "software": {"columns": ["total_packages"], "label": "Total Installed Packages", "kind": "continuous"},
    "migration": {"columns": ["migration_count"], "label": "Migrations Count", "kind": "continuous"},
    "diversity": {"columns": ["jaccard_outlier_score"], "label": "Configuration Outlier Score (Mean Jaccard Distance)", "kind": "continuous"},
}

DEFAULT_LENS_COLOR = {"columns": ["error_count"], "label": "Error Count", "kind": "continuous"}

COLOR_KINDS = ("continuous", "categorical")

AVAILABLE_COLOR_COLUMNS = [
    {"columns": ["error_count"], "label": "Error Count", "kind": "continuous"},
    {"columns": ["fault_count"], "label": "Fault Count", "kind": "continuous"},
    {"columns": ["sync_count"], "label": "Sync Count", "kind": "continuous"},
    {"columns": ["avg_sync_duration_secs"], "label": "Avg Sync Duration (secs)", "kind": "continuous"},
    {"columns": ["pms_failures"], "label": "PMS Failures", "kind": "continuous"},
    {"columns": ["ram_gb"], "label": "RAM (GB)", "kind": "continuous"},
    {"columns": ["disk_gb"], "label": "Disk (GB)", "kind": "continuous"},
    {"columns": ["machine_type"], "label": "Machine Type (Virtual/Physical)", "kind": "continuous"},
    {"columns": ["computer_age_days"], "label": "Computer Age (days)", "kind": "continuous"},
    {"columns": ["days_since_last_sync"], "label": "Days Since Last Sync", "kind": "continuous"},
    {"columns": ["total_packages"], "label": "Total Installed Packages", "kind": "continuous"},
    {"columns": ["migration_count"], "label": "Migrations Count", "kind": "continuous"},
    {"columns": ["days_since_last_migration"], "label": "Days Since Last Migration", "kind": "continuous"},
    {"columns": ["jaccard_outlier_score"], "label": "Configuration Outlier Score (diversity)", "kind": "continuous"},
    {"columns": ["software_drift_score"], "label": "Software Drift Score (software)", "kind": "continuous"},
]

AVAILABLE_METRIC_COLUMNS = [
    {"name": "error_count", "label": "Error Count"},
    {"name": "fault_count", "label": "Fault Count"},
    {"name": "sync_count", "label": "Sync Count"},
    {"name": "avg_sync_duration_secs", "label": "Avg Sync Duration (secs)"},
    {"name": "pms_failures", "label": "PMS Failures"},
    {"name": "ram_gb", "label": "RAM (GB)"},
    {"name": "disk_gb", "label": "Disk (GB)"},
    {"name": "machine_type", "label": "Machine Type (Virtual/Physical)"},
    {"name": "computer_age_days", "label": "Computer Age (days)"},
    {"name": "days_since_last_sync", "label": "Days Since Last Sync"},
    {"name": "total_packages", "label": "Total Installed Packages"},
    {"name": "migration_count", "label": "Migrations Count"},
    {"name": "days_since_last_migration", "label": "Days Since Last Migration"},
    {"name": "jaccard_outlier_score", "label": "Configuration Outlier Score (diversity)"},
    {"name": "software_drift_score", "label": "Software Drift Score (software)"},
]
