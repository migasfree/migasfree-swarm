import logging

# Can be resolved inside pgadmin4 container
try:
    from config import CONSOLE_LOG_FORMAT_JSON, CONSOLE_LOG_LEVEL, JSON_LOGGER  # type: ignore
except ImportError:
    JSON_LOGGER = False
    CONSOLE_LOG_LEVEL = logging.INFO
    CONSOLE_LOG_FORMAT_JSON = ""

try:
    import gunicorn  # type: ignore
    from gunicorn.glogging import Logger  # type: ignore

    gunicorn.SERVER_SOFTWARE = "Python"
except ImportError:
    class Logger:  # type: ignore
        def setup(self, cfg):
            pass

# Include the authenticated user identity in the access log.
# %({x-remote-user}o)s reads the X-Remote-User response header set by pgAdmin
# for authenticated requests; unauthenticated requests log '-'.
access_log_format = (
    '%(h)s %(l)s %({x-remote-user}o)s %(t)s "%(r)s" %(s)s %(b)s '
    '"%(f)s" "%(a)s"'
)


class HealthCheckFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        return '/misc/ping' not in msg and '"GET /health' not in msg


class CustomLogger(Logger):
    def setup(self, cfg):
        super().setup(cfg)
        self.access_log.addFilter(HealthCheckFilter())


logger_class = CustomLogger

if JSON_LOGGER:
    logconfig_dict = {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {"level": CONSOLE_LOG_LEVEL, "handlers": []},
        "loggers": {
            "gunicorn.error": {
                "level": CONSOLE_LOG_LEVEL,
                "handlers": ["error_console"],
                "propagate": True,
                "qualname": "gunicorn.error",
            },
            "gunicorn.access": {
                "level": CONSOLE_LOG_LEVEL,
                "handlers": ["console"],
                "propagate": True,
                "qualname": "gunicorn.access",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "stream": "ext://sys.stdout",
            },
            "error_console": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "stream": "ext://sys.stderr",
            },
        },
        "formatters": {
            "json": {
                "class": "jsonformatter.JsonFormatter",
                "format": CONSOLE_LOG_FORMAT_JSON,
            },
        },
    }
