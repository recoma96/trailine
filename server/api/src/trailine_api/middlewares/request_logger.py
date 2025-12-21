import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from trailine_api.common.logger import request_id_ctx



log = logging.getLogger("app.http")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        rid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token = request_id_ctx.set(rid)

        start_time = time.perf_counter()

        common_logging_payload = {
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host if request.client else None,
        }

        log.info(
            "HTTP-REQUEST",
            extra=common_logging_payload,
        )

        try:
            response: Response = await call_next(request)
        except Exception:
            log.exception(
                "HTTP-REQUEST-ERROR",
                extra=common_logging_payload
            )
            raise
        finally:
            end_time = time.perf_counter()
            process_time = end_time - start_time
            request_id_ctx.reset(token)

        log.info(
            "HTTP-RESPONSE",
            extra=common_logging_payload | {
                "status_code": response.status_code,
                "process_time": round(process_time, 4),
            }
        )

        # response.headers["X-Request-ID"] = rid request_id 추출이 안되서 일단 주석 처리
        return response
