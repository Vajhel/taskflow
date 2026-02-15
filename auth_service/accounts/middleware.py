import logging
import time

logger = logging.getLogger('http')


class RequestLoggingMiddleware:
    """Middleware для логирования HTTP-подключений: время, IP-адрес клиента."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        client_ip = self._get_client_ip(request)

        response = self.get_response(request)

        duration = time.time() - start_time
        logger.info(
            'HTTP %s %s | IP: %s | Status: %s | Duration: %.3fs',
            request.method,
            request.get_full_path(),
            client_ip,
            response.status_code,
            duration,
        )

        return response

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
