
import logging

from django.conf import settings

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object

log = logging.getLogger(__name__)
LOG_REQUESTS_SETTING = 'GALAXY_LOG_REQUESTS'


class LogRequestMiddleware(MiddlewareMixin):
    def process_response(self, request, response):

        if not getattr(settings, LOG_REQUESTS_SETTING, False):
            return response
        # Don't log favicon
        if 'favicon' in request.path:
            return response
        # TODO: config option to disable

        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        referer = request.META.get('HTTP_REFERER', '')

        user = getattr(request, 'user', None)
        user_id = getattr(user, 'pk', None) or getattr(user, 'id', None)

        message = 'method=%s path=%s status=%s'
        args = (request.method, request.path, response.status_code)

        if user_id:
            message += ' user=%s'
            args += (user_id,)

        extra = {'http_method': request.method,
                 'http_url_path': request.path,
                 'http_status_code': response.status_code,
                 'http_user_agent': user_agent,
                 'http_referer': referer}

        used_auth = getattr(request, 'successful_authenticator', None)
        extra['used_auth'] = used_auth
        # extra.update(request.META)

        log.info(message, *args, extra=extra)

        return response
