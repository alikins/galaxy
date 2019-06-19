# (c) 2012-2018, Ansible by Red Hat
#
# This file is part of Ansible Galaxy
#
# Ansible Galaxy is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by
# the Apache Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Ansible Galaxy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Apache License for more details.
#
# You should have received a copy of the Apache License
# along with Galaxy.  If not, see <http://www.apache.org/licenses/>.

from django.conf import settings
from django.contrib import admin
from django.views.generic import TemplateView
from django.urls import include, re_path as url

from rest_framework.schemas import get_schema_view
from rest_framework.renderers import JSONOpenAPIRenderer, OpenAPIRenderer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, DjangoModelPermissionsOrAnonReadOnly
# from galaxy.api import views
# from galaxy.api.permissions import ModelAccessPermission
import logging
log = logging.getLogger(__name__)

admin.autodiscover()

schema_view = get_schema_view(
    title='Galaxy API',
    url='https://galaxy.ansible.com/api/',
    # patterns=api_urls,
    # patterns=schema_api_patterns,
    # urlconf='galaxy.api.urls',
    renderer_classes=[OpenAPIRenderer, JSONOpenAPIRenderer],
    # permission_classes=[AllowAny],
    permission_classes=[IsAuthenticatedOrReadOnly],
    # permission_classes=[DjangoModelPermissionsOrAnonReadOnly],
)


urlpatterns = [
    url(r'^accounts/', include('allauth.urls')),
    url(r'', include('galaxy.api.urls')),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(settings.ADMIN_URL_PATTERN, admin.site.urls),
    url(r'^robots\.txt$', TemplateView.as_view(template_name="robots.txt",
                                               content_type='text/plain')),
    url(r'', include('django_prometheus.urls')),
    url(r'', include('galaxy.main.urls')),
    url(r'^schema/', schema_view),
]

if settings.DEBUG and 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

    log.debug('urlpatterns: %s', urlpatterns)
