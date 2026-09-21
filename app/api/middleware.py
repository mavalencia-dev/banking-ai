import logging
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


logger = logging.getLogger(__name__)


class CorrelationIdMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        correlation_id = request.headers.get(
            "X-Correlation-ID",
            str(uuid.uuid4()),
        )

        logger.info(
            "Request started | correlation_id=%s | method=%s | path=%s",
            correlation_id,
            request.method,
            request.url.path,
        )

        response = await call_next(request)

        response.headers[
            "X-Correlation-ID"
        ] = correlation_id

        logger.info(
            "Request completed | correlation_id=%s | status=%s",
            correlation_id,
            response.status_code,
        )

        return response