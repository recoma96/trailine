import logging
import json
import sys
from contextvars import ContextVar
from datetime import datetime, timezone

from trailine_api.settings import Settings


request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


class JsonLoggingFormater(logging.Formatter):
    STANDARD_ATTRS = {
        "path", "method", "status_code", "process_time", "client", "process", "processName",
    }

    def format(self, record: logging.LogRecord) -> str:
        if Settings.RUN_MODE == "dev" and record.exc_info:
            return self._format_dev_exception(record)
        return self._format_json_payload(record)

    def _format_dev_exception(self, record: logging.LogRecord) -> str:
        """
        개발 환경에서 예외 발생 시, 에러 내용을 보기 좋기 출력하기 위해
        별도 의 프로세스를 통해 출럭하는 함수
        """
        # 기본 포맷 설정 (시간 - 레벨 - 로거 - 메시지)
        record.message = record.getMessage()
        record.asctime = self.formatTime(record, self.datefmt)
        log_entry = f"{record.asctime} [{record.levelname}] {record.name}: {record.message}"

        if record.exc_info:
            if not log_entry.endswith("\n"):
                log_entry += "\n"
            log_entry += self.formatException(record.exc_info)

        if record.stack_info:
            if not log_entry.endswith("\n"):
                log_entry += "\n"
            log_entry += self.formatStack(record.stack_info)

        return log_entry

    def _format_json_payload(self, record: logging.LogRecord) -> str:
        """
        개발환경 + 예외를 제외한 일반적인 경우의 JSON 스타일의 로그 형태
        """
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
