import logging


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
