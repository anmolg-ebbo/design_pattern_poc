import json
import logging
import logging.config
import sys
import traceback
from starlette.datastructures import Headers
import pydash

config = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "maskfilter": {
            "()": "RedactingHeaderFilter",
            "patterns": ["user.email", "authorization", "email"],
        }
    },
    "formatters": {
        "plaintext": {
            "format": "[%(asctime)s] %(process)d %(levelname)s %(name)s:%(funcName)s:%(lineno)s - %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "plaintext",
            "level": "INFO",
            "stream": "ext://sys.stdout",
            "filters": ["maskfilter"],
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
    "loggers": {
        "uvicorn": {"level": "INFO"},
        "fastapi": {"level": "INFO"},
        "mongodb": {"level": "INFO"},
    },
}

class RedactingHeaderFilter(logging.Filter):
    def __init__(self, patterns):
        super(RedactingHeaderFilter, self).__init__()
        self._patterns = patterns

    def filter(self, record):
        if record.levelname != "ERROR":
            if isinstance(record.args, Headers):
                header_log = dict(record.args.items())
                if "user" in header_log:
                    try:
                        header_log["user"] = json.loads(header_log["user"])
                    except:
                        pass
                for pattern in self._patterns:
                    if pydash.has(header_log, pattern):
                        pydash.unset(header_log, pattern)
                record.msg = f"{record.msg} {json.dumps(header_log)}"
        else:
            error_type, value, tb = sys.exc_info()
            trace = traceback.format_tb(tb, None) + traceback.format_exception_only(
                error_type, value
            )
            record.msg = (
                record.msg + f" trace: {trace} value: {value} type: {error_type}"
            )
        return True

class Logging:
    def __init__(self):
        logging.config.dictConfig(config)

    @staticmethod
    def get_logger(name: str):
        return logging.getLogger(name)