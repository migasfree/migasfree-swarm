import logging

try:
    from celery.signals import after_setup_logger, after_setup_task_logger
except ImportError:
    after_setup_logger = None
    after_setup_task_logger = None


class HealthCheckFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if record.args and len(record.args) >= 3:
            method = record.args[1]
            path = record.args[2]
            if method == "GET" and path in ("/", "/health"):
                return False
        msg = record.getMessage()
        if '"GET / HTTP/' in msg or '"GET /health' in msg:
            return False
        return True


class CeleryRoutineTaskFilter(logging.Filter):
    IGNORED_TASKS = (
        "migasfree.stats.tasks.alerts",
        "migasfree.core.tasks.process_notification_queue",
    )

    def filter(self, record: logging.LogRecord) -> bool:
        # Never filter warnings, errors or fatal messages
        if record.levelno >= logging.WARNING:
            return True

        msg = record.getMessage()
        for task_name in self.IGNORED_TASKS:
            if task_name in msg and ("received" in msg or "succeeded in" in msg):
                return False
        return True


def _attach_task_filter(logger):
    if logger:
        task_filter = CeleryRoutineTaskFilter()
        logger.addFilter(task_filter)
        for handler in getattr(logger, "handlers", []):
            handler.addFilter(task_filter)


if after_setup_logger and after_setup_task_logger:
    @after_setup_logger.connect
    @after_setup_task_logger.connect
    def setup_celery_task_filters(logger=None, **kwargs):
        _attach_task_filter(logger)

# Also attach directly to celery standard loggers
for _name in ("celery", "celery.task", "celery.worker.strategy", "celery.app.trace"):
    _attach_task_filter(logging.getLogger(_name))
