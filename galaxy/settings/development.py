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
# Django settings for galaxy project.

import os

from .default import *  # noqa
from .default import LOGGING
from .default import REST_FRAMEWORK


# =========================================================
# Django Core Settings
# =========================================================

DEBUG = True

ALLOWED_HOSTS = ['*']

# For request_id middleware
# https://github.com/dabapps/django-log-request-id
GENERATE_REQUEST_ID_IF_NOT_IN_HEADER = True
LOG_REQUEST_ID_HEADER = "HTTP_X_REQUEST_ID"
REQUEST_ID_RESPONSE_HEADER = "X-GALAXY-REQUEST-ID"
# LOG_REQUESTS = False

# Application definition
# ---------------------------------------------------------

INSTALLED_APPS += (  # noqa: F405
    'debug_toolbar',
)

MIDDLEWARE += [  # noqa: F405
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Database
# ---------------------------------------------------------

DATABASES = {
    'default': {
        'NAME': 'galaxy',
        'USER': 'galaxy',
        'PASSWORD': 'galaxy',
        'HOST': 'postgres',
        'PORT': 5432,
        'CONN_MAX_AGE': None,
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
    }
}

REST_FRAMEWORK.update(
    {'DEFAULT_AUTHENTICATION_CLASSES':
     ('rest_framework.authentication.TokenAuthentication',
      'rest_framework.authentication.SessionAuthentication')
     }
)

# Create default alias for worker logging
DATABASES['logging'] = DATABASES['default'].copy()

# Email settings
# ---------------------------------------------------------

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'

EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'var', 'email')  # noqa: F405

# =========================================================
# Third Party Apps Settings
# =========================================================

# Debug Toolbar
# ---------------------------------------------------------

DEBUG_TOOLBAR_PATCH_SETTINGS = False

# Celery settings
# ---------------------------------------------------------

BROKER_URL = 'amqp://galaxy:galaxy@rabbitmq:5672/galaxy'

# Redis
# ---------------------------------------------------------

REDIS_HOST = 'redis'
REDIS_PORT = 6379

# InfluxDB
# ---------------------------------------------------------

INFLUX_DB_HOST = 'influxdb'
INFLUX_DB_PORT = 8086
INFLUX_DB_USERNAME = 'admin'
INFLUX_DB_PASSWORD = 'admin'
INFLUX_DB_UI_EVENTS_DB_NAME = 'galaxy_metrics'

# =========================================================
# Galaxy Settings
# =========================================================

SITE_ENV = 'DEV'

SITE_NAME = 'localhost'

WAIT_FOR = [
    {'host': 'postgres', 'port': 5432},
    {'host': 'rabbitmq', 'port': 5672},
    {'host': 'influxdb', 'port': 8086},
]

STATIC_ROOT = ''

LOGGING['formatters']['verbose'] = {
    # request_id is added by the request_id filter on the
    # console handler (and others)
    'format': '[%(asctime)s %(request_id)-0.10s %(levelname)s] %(name)s %(module)s.%(funcName)s:%(lineno)d - %(message)s',   # noqa
    'django_server': {
        '()': 'django.utils.log.ServerFormatter',
        'format': '[%(server_time)s] %(message)s - %(request_id)s',
    },
}

# add request id to console handler so request_id is populated
LOGGING['handlers']['console']['filters'] = ['request_id']

# root logger
LOGGING['loggers'][''] = {
    'level': 'DEBUG',
    'handlers': ['console'],
}

LOGGING['loggers']['pulpcore'] = {
    'level': 'DEBUG',
    'handlers': ['console'],
    # 'propagate': False,
}

LOGGING['loggers']['pulpcore.app'] = {
    'level': 'DEBUG',
    'handlers': ['console'],
    # 'propagate': False,
}

LOGGING['loggers']['pulpcore.tasking.services.worker_watcher'] = {
    'level': 'INFO',
}

LOGGING['loggers']['rq.worker'] = {
    'level': 'INFO',
}

LOGGING['loggers']['django.request'] = {
    'level': 'DEBUG',
    'handlers': ['console']
}

LOGGING['loggers']['django.security'] = {
    'level': 'DEBUG',
    'handlers': ['console']
}

LOGGING['loggers']['django.server'] = {
    'level': 'DEBUG',
    'handlers': ['console']
}

LOGGING['loggers']['allauth'] = {
    'level': 'DEBUG',
    'handlers': ['console'],
}
