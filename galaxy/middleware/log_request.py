
import logging

from django.conf import settings

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object

log = logging.getLogger(__name__)
LOG_REQUESTS_SETTING = 'GALAXY_LOG_REQUESTS'


def extra_from_resolver_match(resolver_match):
    # nested inside 'resolver' key to avoid clobbering 'func', 'args'
    extra = {'http_request_resolver': {}}

    for attr in ('args',
                 'kwargs',
                 'url_name',
                 # 'app_name',
                 'app_names',
                 # 'namespace',
                 'namespaces',
                 'view_name'):
        extra['http_request_resolver'][attr] = \
            getattr(resolver_match, attr, None)

    return extra


def extra_from_request(request):
    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
    referer = request.META.get('HTTP_REFERER', '')
    remote_addr = request.META.get('REMOTE_ADDR', '')
    server_name = request.META.get('SERVER_NAME', '')
    server_port = request.META.get('SERVER_PORT', '')
    query_string = request.META.get('QUERY_STRING', '')
    # content_type = request.META.get('CONTENT_TYPE', '')
    content_length = request.META.get('CONTENT_LENGTH', '')

    user_obj = getattr(request, 'user', None)
    user_name = user_obj.username
    user_id = getattr(user_obj, 'pk', None) or \
        getattr(user_obj, 'id', None)

    cookies_obj = getattr(request, 'COOKIES', {})
    cookies_dict = dict(cookies_obj.items())

    query_param_obj = getattr(request, 'GET', {})
    query_params = query_param_obj.items()

    # To see all query params, even dupes
    # if query_param_obj:
    #    for query_param_item in query_param_obj.lists():
    #        query_params.append(query_param_item)

    request_extra = {'http_method': request.method,
                     'http_url_path': request.path,
                     'http_query_string': query_string,
                     'http_query_params': query_params,
                     'http_user_agent': user_agent,
                     'http_user_name': user_name,
                     'http_user_id': user_id,
                     'http_referer': referer,
                     # 'http_content_type': content_type,
                     'http_content_length': content_length,
                     'http_remote_addr': remote_addr,
                     'http_server_name': server_name,
                     'http_server_port': server_port,
                     # 'http_request_environ': request.environ,
                     }

    if cookies_dict.get('sessionid'):
        request_extra['http_session_id'] = cookies_dict['sessionid']

    resolver_extra = extra_from_resolver_match(request.resolver_match)
    request_extra.update(resolver_extra)

    request_extra['http_get_host'] = request.get_host()

    return request_extra


class LogRequestMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        extra = extra_from_request(request)
        log.debug('request=%s, view_func=%s, view_args=%s, view_kwargs=%s',
                  request, view_func, view_args, view_kwargs, extra=extra)

        return None

    def process_exception(self, request, exception):
        extra = extra_from_request(request)
        log.debug('process_exception request=%s, exception=%s',
                  request, exception, extra=extra)
        return None

    def process_response(self, request, response):

        if not getattr(settings, LOG_REQUESTS_SETTING, False):
            return response
        # Don't log favicon
        if 'favicon' in request.path:
            return response

        extra = {}

        request_extra = extra_from_request(request)

        response_extra = {
            'http_status_code': response.status_code,
        }

        accepted_media_type = getattr(response, 'accepted_media_type', '')
        response_extra['http_response_media_type'] = accepted_media_type

        extra.update(request_extra)
        extra.update(response_extra)

        # EVERYTHING
        # extra['http_response_attrs'] = dir(response)
        # extra['http_request_attrs'] = dir(request)
        # extra['_http_response_dict'] = getattr(response, '__dict__', {})
        # extra['_http_request_dict'] = getattr(request, '__dict__', {})
        # extra['self_attrs'] = dir(self)

        message = 'method=%s path=%s status=%s'
        args = (request.method, request.path, response.status_code)

        user_name = request_extra.get('user_name')
        user_id = request_extra.get('user_id')

        if user_name:
            message += ' user=%s'
            args += (user_name,)

        if user_id:
            message += ' user_id=%s'
            args += (user_id,)

        log.info(message, *args, extra=extra)

        return response
