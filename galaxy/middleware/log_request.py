
import logging

from django.conf import settings

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object

# TODO: possibly split this into three separate middleware classes?
#       That would let us tweak the ordering in MIDDLEWARE chain a bit
# TODO: port to new middleware API?
# TODO: maybe make some of the extra collection code configurable, and
#       possibly based on the log level. ie, don't collect the process_view
#       args at INFO level, but do at DEBUG level.

log = logging.getLogger(__name__)
# If we log from process_response, adding info from the
# request and the response. Default is True.
LOG_REQUESTS_SETTING = 'GALAXY_LOG_REQUESTS'

# If we should log the request info via process_view, ie, before the
# response is generated.
LOG_REQUESTS_VIEW_SETTING = 'GALAXY_LOG_REQUESTS_VIEW'
# if we should include args to process_view (view_func, view_args, view_kwargs)
# in view logging extra. Only applies if GALAXY_LOG_REQUESTS_VIEW is true.
# default is False
LOG_REQUESTS_VIEW_EXTRA_SETTING = 'GALAXY_LOG_REQUESTS_VIEW_EXTRA'

# If we log from process_exception or not. Default is False.
LOG_REQUESTS_EXPECTIONS_SETTING = 'GALAXY_LOG_REQUESTS_EXCEPTIONS'


def extra_from_resolver_match(resolver_match):
    # nested inside 'resolver' key to avoid clobbering 'func', 'args'
    # extra = {'http_request_resolver': {}}
    resolver_extra = {}

    for attr in ('args',
                 'kwargs',
                 'url_name',
                 # 'app_name',
                 'app_names',
                 # 'namespace',
                 'namespaces',
                 'view_name'):
        resolver_extra[attr] = \
            getattr(resolver_match, attr, None)

    return resolver_extra


META_PREFIXES = ('HTTP_', 'CONTENT_', 'QUERY_',
                 'REMOTE_', 'REQUEST_', 'SERVER_')


def extra_from_request(request):
    # TODO: maybe easier to just return the whole META dict as
    #       a subdict in request_extra, possibly with config
    #       excluding things.
    # user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
    # referer = request.META.get('HTTP_REFERER', '')
    # remote_addr = request.META.get('REMOTE_ADDR', '')
    # server_name = request.META.get('SERVER_NAME', '')
    # server_port = request.META.get('SERVER_PORT', '')
    # query_string = request.META.get('QUERY_STRING', '')
    # content_type = request.META.get('CONTENT_TYPE', '')
    # content_length = request.META.get('CONTENT_LENGTH', '')

    user_obj = getattr(request, 'user', None)
    user_name = getattr(user_obj, 'username', None)
    user_id = getattr(user_obj, 'pk', None) or \
        getattr(user_obj, 'id', None)

    query_param_obj = getattr(request, 'GET', {})
    query_params = query_param_obj.items()

    post_param_obj = getattr(request, 'GET', {})
    post_params = post_param_obj.items()

    # To see all query params, even dupes
    # if query_param_obj:
    #    for query_param_item in query_param_obj.lists():
    #        query_params.append(query_param_item)

    request_extra = {'scheme': request.scheme,
                     # 'method': request.method,
                     'url_path': request.path,
                     'url_path_info': request.path_info,
                     'url_full_path': request.get_full_path(),
                     # 'url_full_path_info': request.get_full_path_info(),
                     'url_absolute': request.build_absolute_uri(),
                     # 'query_string': query_string,
                     'query_params': query_params,
                     'post_parans': post_params,
                     # 'user_agent': user_agent,
                     'user_name': user_name,
                     'user_id': user_id,
                     # 'referer': referer,
                     # 'http_content_type': content_type,
                     # 'content_length': content_length,
                     # 'remote_addr': remote_addr,
                     # 'server_name': server_name,
                     # 'server_port': server_port,
                     # 'http_request_environ': request.environ,
                     }

    # Just get expected META fields, including http headers
    meta_extra = {}
    for meta_key in request.META:
        for meta_prefix in META_PREFIXES:
            if meta_key.startswith(meta_prefix):
                meta_extra[meta_key] = request.META[meta_key]

    request_extra['META'] = meta_extra

    cookies_obj = getattr(request, 'COOKIES', {})
    cookies_dict = dict(cookies_obj.items())

    if cookies_dict.get('sessionid'):
        request_extra['session_id'] = cookies_dict['sessionid']

    resolver_extra = extra_from_resolver_match(request.resolver_match)
    request_extra['resolver'] = resolver_extra

    request_extra['get_host'] = request.get_host()

    return request_extra


class LogRequestMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        # GALAXY_LOG_REQUESTS_VIEW is False by default, which means we
        # return here and  dont log from process_view by default
        if not getattr(settings, LOG_REQUESTS_VIEW_SETTING, False):
            return None

        request_extra = extra_from_request(request)
        extra = {'http_request': request_extra}

        if getattr(settings, LOG_REQUESTS_VIEW_EXTRA_SETTING, False):
            view_extra = {
                'view_func': view_func,
                'view_args': view_args,
                'view_kwargs': view_kwargs
            }

            extra['django_view'] = view_extra

        log.debug('request=%s, view_func=%s, view_args=%s, view_kwargs=%s',
                  request, view_func, view_args, view_kwargs, extra=extra)

        return None

    def process_exception(self, request, exception):
        # GALAXY_LOG_REQUESTS_EXCEPTIONS is False by default, so don't do
        # any additional logging from process_exception by default.
        if not getattr(settings, LOG_REQUESTS_EXPECTIONS_SETTING, False):
            return None

        request_extra = extra_from_request(request)
        extra = {'http_request': request_extra}

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
            'status_code': response.status_code,
        }

        accepted_media_type = getattr(response, 'accepted_media_type', '')
        response_extra['media_type'] = accepted_media_type

        extra['http_request'] = request_extra
        extra['http_response'] = response_extra

        # EVERYTHING
        # extra['_http_response_dict'] = getattr(response, '__dict__', {})
        # extra['_http_request_dict'] = getattr(request, '__dict__', {})
        # extra['_self_attrs'] = dir(self)

        # TODO: might as well make this look more like a http log line
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
