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
import dj_database_url

from .default import *  # noqa


# =========================================================
# Django Core Settings
# =========================================================

DEBUG = True

ALLOWED_HOSTS = ['*']

# https://github.com/dabapps/django-log-request-id
LOG_REQUEST_ID_HEADER = "HTTP_X_REQUEST_ID"
GENERATE_REQUEST_ID_IF_NOT_IN_HEADER = True
REQUEST_ID_RESPONSE_HEADER = "X-GALAXY-REQUEST-ID"
GALAXY_LOG_REQUESTS = True
LOG_REQUESTS = False

shared_log_format = '[%(asctime)s %(request_id)s %(process)d:%(threadName)s %(levelname)s] %(name)s %(filename)s %(funcName)s:%(lineno)d'
default_log_format = '%s : %s' % (shared_log_format, '%(message)s')

sql_log_format = shared_log_format + ': ====== begin ======\n%(sql)s\n====== end ======'


# sql_log_format = '[%(asctime)s %(levelname)s] %(name)s %(sql)s'

LOGGING = {
    'version': 1,

    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': default_log_format,
        },
        'simple': {
            'format': '%(levelname)s %(message)s',
        },
        'json': {
            '()': 'jog.JogFormatter',
            'format': default_log_format,
        },
        'django_server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[%(server_time)s] %(message)s - %(request_id)s',
        },
        'django_db_sql': {
            '()': 'galaxy.common.logutils.DjangoDbSqlFormatter',
            # 'format': shared_log_format,
            'format': sql_log_format,
        },
        'pprint': {
            '()': 'galaxy.common.logutils.PPrintFormatter',
            'indent': 4,
        },
        'color_verbose': {
            '()': 'color_debug.color_debug.ColorFormatter',
            'format': '[%(asctime)s %(levelname)-0.1s] %(name)s %(funcName)s:%(lineno)-3d - %(message)s - %(request_id)s',
            # default_color_by_attr: 'module'
            'default_color_by_attr': 'request_id',
            # default_color_by_attr: msg
            'auto_color': True,
            'color_groups': [
                ['process', ['processName']],
                ['levelname', ['levelname']],
                ['funcName', ['lineno']],
            ]
            # messages logged with the same 'msg' share a color
            #  - ['msg', ['message']]
            #  - ['name', ['name', 'levelname']]
        },

    },

    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'request_id': {
            '()': 'log_request_id.filters.RequestIDFilter'
        },
        'django_db_sql_celery_filter': {
            '()': 'galaxy.common.logutils.DjangoDbSqlCeleryFilter',
        },
    },

    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            # 'formatter': 'verbose',
            # 'formatter': 'json',
            # 'formatter': 'pprint',
            'formatter': 'color_verbose',
            'filters': ['request_id'],
            # 'filters': ['require_debug_true'],
            # 'filters': ['require_debug_false'],
        },
        'celery_console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            # 'formatter': 'verbose',
            # 'formatter': 'json',
            # 'formatter': 'pprint',
            'formatter': 'color_verbose',
            'filters': ['request_id'],
            # 'filters': ['require_debug_true'],
            # 'filters': ['require_debug_false'],
        },
        'import_task': {
            'level': 'DEBUG',
            'class': 'galaxy.common.logutils.ImportTaskHandler',
            'formatter': 'simple',
            # 'formatter': 'verbose',
        },
        'django_server_console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'django_server',
            'filters': ['request_id'],
        },
        'django_server_request_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': '/galaxy/django_server.log',
            'formatter': 'django_server',
            'filters': ['request_id'],
            # 'filters': ['require_debug_true'],
        },
        'django_server_request_debug_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': '/galaxy/django_debug_server.log',
            'formatter': 'pprint',
            'filters': ['request_id'],
            # 'filters': ['require_debug_true'],
        },
        'galaxy_debug_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': '/galaxy/galaxy_debug.log',
            'formatter': 'pprint',
            'filters': ['request_id'],
            # 'filters': ['require_debug_true'],
        },
        'django_db_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': '/galaxy/django_db.log',
            'formatter': 'django_db_sql',
            # 'filters': ['django_db_sql_celery_filter'],
            # 'formatter': 'verbose',
            'filters': ['django_db_sql_celery_filter',
                        'require_debug_true',
                        'request_id'],
        },
#        'django_db_color_file': {
#            'level': 'DEBUG',
#            'class': 'logging.handlers.WatchedFileHandler',
#            'filename': '/galaxy/django_db_color.log',
#            'formatter': 'color_verbose',
#            'filters': ['django_db_sql_celery_filter',
#                        'require_debug_true',
#                        'request_id'],
#        }
    },

    'loggers': {
        # root logger
        '': {
            'handlers': ['console'],
            # 'level': 'INFO',
            'level': 'DEBUG',
            # 'propagate': True,
        },
        'django.request': {
            # 'handlers': ['mail_admins'],
            'handlers': ['console'],
            # 'level': 'INFO',
            'level': 'DEBUG',
            'propagate': True,
        },
        'django': {
            # 'handlers': ['console'],
            'handlers': ['django_server_request_file',
                         'django_server_request_debug_file',
                         'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.db': {
            # 'handlers': ['django_db_file'],
            'handlers': ['console'],
            # 'level': 'INFO',
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['django_db_file'],
            # 'handlers': ['console'],
            'level': 'INFO',
            # 'level': 'DEBUG',
            'propagate': False,
            # 'propagate': True,
        },
#        'django.server': {
#            'handlers': ['django_server_request_file',
#                         'django_server_request_debug_file',
#                         'console'],
            # 'level': 'INFO',
#            'level': 'DEBUG',
            # 'propagate': False,
#        },
        'galaxy.api': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'galaxy.api.permissions': {
            'handlers': ['console'],
            'level': 'INFO',
            # 'level': 'DEBUG',
            'propagate': True,
        },
        'galaxy.api.access': {
            'handlers': ['console'],
            # 'level': 'INFO',
            'level': 'DEBUG',
            'propagate': True,
        },
        'galaxy.api.throttling': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'galaxy.accounts': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'galaxy.main': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'galaxy.models': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'galaxy.worker': {
            'handlers': ['console', 'celery_console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'galaxy.worker.tasks.import_repository': {
            'handlers': ['import_task'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'galaxy.middleware.log_request': {
            'handlers': ['django_server_request_debug_file'],
            'level': 'DEBUG',
        },
        # if LOG_REQUESTS=True, then he django-log-request-id package
        # logs request details to 'log_request_id.middleware'
        'log_request_id.middleware': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'allauth': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'celery': {
            'handlers': ['celery_console'],
            'level': 'DEBUG',
            # 'filters': ['django_db_sql_celery_filter'],
        },
        'celery.beat': {
            'handlers': ['celery_console'],
            'level': 'INFO',
        },
        'github': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    }
}
# Application definition
# ---------------------------------------------------------

INSTALLED_APPS += (  # noqa: F405
    'debug_toolbar',
)

MIDDLEWARE += [  # noqa: F405
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# https://github.com/celery/celery/issues/4326
CELERY_WORKER_HIJACK_ROOT_LOGGER = False
# CELERY_CELERYD_HIJACK_ROOT_LOGGER = False
CELERY_WORKER_LOG_FORMAT = shared_log_format
CELERY_WORKER_TASK_LOG_FORMAT = "[%(asctime)s: %(levelname)s/%(processName)s] %(name)s %(filename)s %(funcName)s:%(lineno)d : [%(task_name)s(%(task_id)s)] %(message)s"

# Database
# ---------------------------------------------------------

# Define GALAXY_DB_URL=postgres://USER:PASSWORD@HOST:PORT/NAME
DATABASES = {
    'default': dj_database_url.config(
        env='GALAXY_DB_URL', conn_max_age=None
    )
}

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

# =========================================================
# Galaxy Settings
# =========================================================

SITE_ENV = 'DEV'

SITE_NAME = 'localhost'

WAIT_FOR = [
    {'host': 'postgres', 'port': 5432},
    {'host': 'rabbitmq', 'port': 5672},
    {'host': 'influxdb', 'port': 8086},
    {'host': 'grafana', 'port': 3000},
    {'host': 'prometheus', 'port': 9090},
]

STATIC_ROOT = ''
