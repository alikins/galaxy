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

shared_log_format = '[%(asctime)s %(process)d:%(threadName)s %(levelname)-0.1s] %(name)s %(filename)s %(funcName)s:%(lineno)d'

# default_log_format = shared_log_format + ' : ' + '%(message)s'
default_log_format = '[%(asctime)s %(process)d:%(threadName)s %(levelname)-0.1s] %(name)s %(filename)s %(funcName)s:%(lineno)d : %(message)s'

sql_log_format = shared_log_format + ': ====== begin ======\n%(sql)s\n====== end ======'

importer_log_format = '[%(asctime)s %(process)05d %(levelname)-0.1s] task:%(task_id)-0.4s %(name)s %(filename)s %(funcName)s:%(lineno)d : %(message)s'


# sql_log_format = '[%(asctime)s %(levelname)s] %(name)s %(sql)s'

LOGGING = {
    'version': 1,

    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': default_log_format,
            # 'format': '%(message)s'
        },
        'verbose_importer': {
            'format': importer_log_format,
            # 'format': '%(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s',
        },
        'django_server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[%(server_time)s] %(message)s',
        },
        #'django_db_sql': {
        #    '()': 'galaxy.common.logutils.DjangoDbSqlFormatter',
            # 'format': shared_log_format,
            # 'format': sql_log_format,
        #}
    },

    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'django_db_sql_celery_filter': {
            '()': 'galaxy.common.logutils.DjangoDbSqlCeleryFilter',
        }
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
            'formatter': 'verbose',
            'stream': 'ext://sys.stdout',
            # 'filters': ['require_debug_true'],
        },
        'import_task': {
            'level': 'DEBUG',
            'class': 'galaxy.common.logutils.ImportTaskHandler',
            'formatter': 'simple',
            # 'formatter': 'verbose',
        },
        # not confident logging to a file will work for celery tasks
        # but hoping they do some queue/event handler stuff internally...
        'import_task_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': '/galaxy/galaxy_import.log',
            # 'formatter': 'simple',
            'formatter': 'verbose_importer',
        },
        'django_server_console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'django_server',
        },
        'django_server_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': '/galaxy/django_server.log',
            'formatter': 'django_server',
            # 'filters': ['require_debug_true'],
        },
        'django_db_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': '/galaxy/django_db.log',
            # 'formatter': 'django_db_sql',
            # 'filters': ['django_db_sql_celery_filter'],
            # 'formatter': 'verbose',
            # 'filters': ['require_debug_true'],
        },
    },

    'loggers': {
        # root logger
        '': {
            'handlers': ['console'],
            # 'level': 'INFO',
            'level': 'DEBUG',
            # 'propagate': True,
            # 'filters': ['require_debug_true'],
        },
        'django.request': {
            'handlers': ['console'],
            # 'level': 'INFO',
            'level': 'DEBUG',
            'propagate': True,
        },
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.db': {
            'handlers': ['django_db_file'],
            'level': 'INFO',
            # 'level': 'DEBUG',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['django_db_file'],
            'level': 'INFO',
            # 'level': 'DEBUG',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['django_server_file'],
            # 'level': 'INFO',
            'level': 'DEBUG',
            # 'propagate': False,
        },
        'galaxy': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
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
            'level': 'INFO',
            # 'level': 'DEBUG',
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
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'galaxy.worker.tasks.import_repository': {
            'handlers': ['import_task', 'import_task_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'allauth': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'celery': {
            'handlers': ['console'],
            'level': 'DEBUG',
            # 'filters': ['django_db_sql_celery_filter'],
        },
        'celery.beat': {
            'handlers': ['console'],
            'level': 'INFO',
        }
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
#CELERY_WORKER_HIJACK_ROOT_LOGGER = False
#CELERY_CELERYD_HIJACK_ROOT_LOGGER = False
#CELERY_WORKER_LOG_FORMAT = shared_log_format
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
