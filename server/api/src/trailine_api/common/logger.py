import logging
import json
import sys
from contextvars import ContextVar
from datetime import datetime, timezone


request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


class JsonLoggingFormater(logging.Formatter):
    STANDARD_ATTRS = {
        "path", "method", "status_code", "process_time", "client", "process", "processName",
    }

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            # "request_id": request_id_ctx.get(), 계속 NULL로 나오고 있음
        }

        for k, v in record.__dict__.items():
            if k in self.STANDARD_ATTRS:
                k = {
                    "process": "pid",
                    "processName": "process_name",
                }.get(k, k)
                payload[k] = v

        # 예외 발생 시
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False)


def setup_logging(level: str = "INFO") -> None:
    root = logging.getLogger()
    root.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonLoggingFormater())

    # Unvicorn 기본 핸들러 중복 방지
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logging.getLogger(name).handlers.clear()
        logging.getLogger(name).propagate = True

    root.handlers.clear()
    root.addHandler(handler)
