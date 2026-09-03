"""
TDA Worker: Scheduled analytics worker for Migasfree.

Runs TDA analysis (Mapper algorithm) on the migasfree database
at configurable intervals. Results are saved as JSON graphs and
HTML visualizations to /data/tda.

Environment variables:
    TDA_SCHEDULE      - Cron-like schedule (default: "0 3 * * *" = 03:00 daily)
"""

import os
import sys
import time
import signal
import logging
import threading
from datetime import datetime

from lens_store import load_all_lenses, load_lens, seed_builtin_lenses

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("migasfree-tda")

# Graceful shutdown
_shutdown = False


def _handle_signal(signum, frame):
    global _shutdown
    logger.info(f"Received signal {signum}, shutting down...")
    _shutdown = True


signal.signal(signal.SIGTERM, _handle_signal)
signal.signal(signal.SIGINT, _handle_signal)


def parse_cron_schedule(schedule_str):
    """
    Simple cron parser: returns seconds until next execution.
    Supports: "minute hour day_of_month month day_of_week"
    For simplicity, only handles fixed hour/minute patterns.
    """
    parts = schedule_str.strip().split()
    if len(parts) != 5:
        logger.warning(f"Invalid cron schedule '{schedule_str}', defaulting to hourly")
        return 3600

    minute, hour = parts[0], parts[1]
    now = datetime.now()

    if minute == "*" and hour == "*":
        return 60  # every minute
    elif hour == "*":
        # Every hour at the given minute
        target_min = int(minute)
        if now.minute >= target_min:
            # next hour
            return (60 - now.minute + target_min) * 60 - now.second
        else:
            return (target_min - now.minute) * 60 - now.second
    else:
        # Specific hour and minute
        target_hour = int(hour)
        target_min = int(minute)
        target = now.replace(hour=target_hour, minute=target_min, second=0, microsecond=0)
        if target <= now:
            # Tomorrow
            target = target.replace(day=target.day + 1)
        diff = (target - now).total_seconds()
        return max(diff, 0)


import threading

# Execution state
_analysis_lock = threading.Lock()
_state = {
    "is_running": False,
    "current_step": "Idle",
    "last_run_started": None,
    "last_run_finished": None,
    "last_run_duration": None,
    "last_error": None,
    "logs": [],
    "lenses": {},  # lens_name -> {status, started, finished, nodes, edges, error, reason}
}


def get_status():
    """Return the current analysis state."""
    return dict(_state)


def _log_event(msg: str):
    """Add a timestamped event log."""
    ts = datetime.now().strftime("%H:%M:%S")
    entry = f"[{ts}] {msg}"
    logger.info(msg)
    if "logs" in _state:
        _state["logs"].append(entry)
        if len(_state["logs"]) > 100:
            _state["logs"] = _state["logs"][-100:]


def get_lens_specs_for_run():
    """
    Determine which lenses to compute on a scheduled run.

    - Only lenses with scheduled=True (default: True) are run.
    """
    return [s for s in load_all_lenses() if s.get("scheduled", True)]


def run_analysis(only_lens=None):
    """Execute TDA analysis for all configured lenses (or a single one)."""
    global _state
    if not _analysis_lock.acquire(blocking=False):
        logger.warning("Analysis already in progress, skipping trigger")
        return False

    _state["is_running"] = True
    _state["current_step"] = "Initializing"
    _state["last_run_started"] = datetime.utcnow().isoformat()
    _state["last_error"] = None
    _state["logs"] = []
    _state["lenses"] = {}
    start_time = time.time()

    output_dir = "/data/tda"

    os.makedirs(output_dir, exist_ok=True)
    seed_builtin_lenses()

    lens_specs = [load_lens(only_lens)] if only_lens else get_lens_specs_for_run()
    lens_specs = [s for s in lens_specs if s]
    lens_names = [s["name"] for s in lens_specs]

    _log_event("Starting TDA analysis pipeline")
    _log_event(f"Lenses ({len(lens_names)}): {', '.join(lens_names)}")

    try:
        from tda_engine import build_feature_matrix, run_mapper

        _state["current_step"] = "Extracting data"
        _log_event("Connecting to PostgreSQL...")

        ran_any = False
        for i, spec in enumerate(lens_specs):
            lens = spec["name"]
            _state["current_step"] = f"Computing lens: {lens} ({i+1}/{len(lens_specs)})"
            _state["lenses"][lens] = {
                "status": "running",
                "started": datetime.utcnow().isoformat(),
            }
            _log_event(f"Computing lens '{lens}'...")
            try:
                # Each lens builds its own feature matrix with its own
                # dataset (attribute prefixes, metrics, scope filters)
                dataset = spec.get("dataset") or {}
                df_lens, fm_lens = build_feature_matrix(
                    None,
                    formula_prefix_ids=dataset.get("formula_prefix_ids"),
                    scope_ids=dataset.get("scope_ids"),
                    metric_columns=dataset.get("metric_columns"),
                    metrics_interval_days=dataset.get("metrics_interval_days"),
                )
                if df_lens.empty or fm_lens.size == 0:
                    _state["lenses"][lens] = {
                        "status": "skipped",
                        "finished": datetime.utcnow().isoformat(),
                        "reason": "no computers with the selected filters",
                    }
                    _log_event(f"⚠ No computers for lens '{lens}' with the selected filters; skipping")
                    continue
                ran_any = True
                _log_event(f"Lens '{lens}': {len(df_lens)} computers × {fm_lens.shape[1] if fm_lens.size else 0} features")
                result = run_mapper(df_lens, fm_lens, lens, spec=spec, output_dir=output_dir)
                n_nodes = result.get('metadata', {}).get('total_nodes', 0)
                n_edges = result.get('metadata', {}).get('total_edges', 0)
                _state["lenses"][lens] = {
                    "status": "done",
                    "finished": datetime.utcnow().isoformat(),
                    "nodes": int(n_nodes),
                    "edges": int(n_edges),
                }
                _log_event(f"✓ Lens '{lens}' generated: {n_nodes} nodes, {n_edges} edges")
            except Exception as e:
                _state["lenses"][lens] = {
                    "status": "error",
                    "finished": datetime.utcnow().isoformat(),
                    "error": str(e),
                }
                _log_event(f"✗ Error in lens '{lens}': {e}")
                logger.error(f"Error running lens '{lens}': {e}", exc_info=True)

        if not ran_any:
            _log_event("Warning: no lens produced a graph (no computer data found)")

    except Exception as e:
        _state["last_error"] = str(e)
        _log_event(f"Fatal error: {e}")
        logger.error(f"Fatal error during analysis: {e}", exc_info=True)
    finally:
        duration = time.time() - start_time
        _state["is_running"] = False
        _state["current_step"] = "Completed"
        _state["last_run_finished"] = datetime.utcnow().isoformat()
        _state["last_run_duration"] = round(duration, 2)
        _log_event(f"TDA analysis complete in {duration:.2f}s")
        _analysis_lock.release()

    return True


def start_scheduler_thread():
    """Start background scheduler loop in a daemon thread."""
    def _loop():
        schedule = os.getenv("TDA_SCHEDULE", "0 3 * * *")

        logger.info(f"TDA Scheduler started (schedule: {schedule})")

        while not _shutdown:
            sleep_secs = parse_cron_schedule(schedule)
            logger.info(f"Next scheduled run in {sleep_secs:.0f} seconds ({sleep_secs / 3600:.1f} hours)")

            waited = 0
            while waited < sleep_secs and not _shutdown:
                time.sleep(min(10, sleep_secs - waited))
                waited += 10

            if not _shutdown:
                run_analysis()

        logger.info("TDA Scheduler stopped")

    t = threading.Thread(target=_loop, daemon=True, name="tda-scheduler")
    t.start()
    return t


if __name__ == "__main__":
    main()
