import logging
import time
import uuid

logger = logging.getLogger("soleline.request")


class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.request_id = str(uuid.uuid4())
        start = time.monotonic()
        response = self.get_response(request)
        response["X-Request-ID"] = request.request_id
        logger.info(
            "request_id=%s method=%s path=%s status=%s duration_ms=%.1f",
            request.request_id,
            request.method,
            request.path,
            response.status_code,
            (time.monotonic() - start) * 1000,
        )
        return response
