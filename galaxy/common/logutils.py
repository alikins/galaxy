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

from __future__ import absolute_import

import json
import logging
import sqlparse
import pprint

import jog
from jog import elk

from galaxy import constants


class ImportTaskAdapter(logging.LoggerAdapter):
    def __init__(self, logger, task_id):
        super(ImportTaskAdapter, self).__init__(logger, {'task_id': task_id})

    def process(self, msg, kwargs):
        if self.extra:
            if 'extra' not in kwargs:
                kwargs.update({'extra': {}})
            for key, value in self.extra.items():
                kwargs['extra'][key] = value
        return msg, kwargs


class ContentTypeAdapter(logging.LoggerAdapter):
    def __init__(self, logger, content_type, content_name=None):
        super(ContentTypeAdapter, self).__init__(logger, {
            'content_type': content_type,
            'content_name': content_name,
        })

    def process(self, msg, kwargs):
        if self.extra:
            if 'extra' not in kwargs:
                kwargs.update({'extra': {}})
            for key, value in self.extra.items():
                kwargs['extra'][key] = value
        return msg, kwargs


class ImportTaskHandler(logging.Handler):
    def emit(self, record):
        # type: (logging.LogRecord) -> None
        from galaxy.main import models

        lint = {
            'is_linter_rule_violation': False,
            'linter_type': None,
            'linter_rule_id': None,
            'rule_desc': None,
            'content_name': '',
        }
        if set(lint.keys()).issubset(vars(record).keys()):
            lint['is_linter_rule_violation'] = record.is_linter_rule_violation
            lint['linter_type'] = record.linter_type
            lint['linter_rule_id'] = record.linter_rule_id
            lint['rule_desc'] = record.rule_desc
            lint['content_name'] = record.content_name

        models.ImportTaskMessage.objects.using('logging').create(
            task_id=record.task_id,
            message_type=constants.ImportTaskMessageType.from_logging_level(
                record.levelno).value,
            message_text=record.msg,
            is_linter_rule_violation=lint['is_linter_rule_violation'],
            linter_type=lint['linter_type'],
            linter_rule_id=lint['linter_rule_id'],
            rule_desc=lint['rule_desc'],
            content_name=lint['content_name'],
        )


class IndentedJSONEncoder(json.JSONEncoder):
    '''A JSONEncoder that defaults to indented "pretty" output'''

    def __init__(self, *args, **kwargs):
        kwargs['indent'] = 2
        super(IndentedJSONEncoder, self).__init__(*args, **kwargs)

    # We don't want to lose a log because it contains
    # a object we don't know how to encode. Instead,
    # convert it to a string.
    def default(self, o):
        return str(o)


class JogIndentedJSONFormatter(jog.JogFormatter):
    def __init__(self, fmt=None, datefmt=None, style=None,
                 fn=None, json_encoder_cls=None):
        json_encoder_cls = json_encoder_cls or IndentedJSONEncoder
        super(JogIndentedJSONFormatter, self).__init__(fmt=fmt,
                                                       datefmt=datefmt,
                                                       style=style,
                                                       fn=fn)
        self.json_encoder_cls = json_encoder_cls


# c&p of git@github.com:braedon/python-jog.git since it's not easy
# to override the json encoder
class JSONFormatter(logging.Formatter):

    def __init__(self, fmt=None, datefmt=None,
                 style=None, fn=elk.format_log,
                 json_encoder_cls=None, indent=None):
        self.fn = fn
        kwargs = {
            'fmt': fmt,
            'datefmt': datefmt
        }
        # Python2 logging.Formatter doesn't support the `style` parameter so
        # only pass it on if passed to us.
        if style:
            kwargs['style'] = style
        super(JSONFormatter, self).__init__(**kwargs)

        # self.json_encoder_cls = json_encoder_cls or IndentedJSONEncoder
        self.json_encoder_cls = json_encoder_cls or jog.LoggingJSONEncoder
        self.indent = indent

    def format(self, record):
        # Call this first as it changes the record, e.g. formatting exceptions.
        # For efficency's sake, we use these changes rather than performing
        # them ourselves.
        plain_text_log = super(JSONFormatter, self).format(record)

        fields = record.__dict__.copy()

        field_updates = {}

        message_format = fields.pop('msg')
        # If the message is a dict use it directly
        if isinstance(message_format, (dict,)):
            del fields['message']
            field_updates.update(message_format)

        # Otherwise it's a normal log record, so we need to format it
        else:
            # Preserve the unformatted message string.
            # Useful for selecting selecting all instances of a log,
            # regardless of the variables substituted in.
            field_updates['message_format'] = message_format

            # The format args can be either args (list) or kwargs (dict)
            # so split into different fields to simplify handling later.
            if 'args' in fields:
                args = fields.pop('args')
                if isinstance(args, (dict,)):
                    field_updates['message_kwargs'] = args
                else:
                    field_updates['message_args'] = args

            # The formatted message itself
            field_updates['message'] = record.getMessage()

            # The full formatted non-structured log line.
            # Useful if you need to tail the logs.
            field_updates['log'] = plain_text_log

        log = fields
        log.update(field_updates)

        # Drop empty fields
        log = {k: v for k, v in log.items() if v}

        log = self.fn(log)

        return json.dumps(log, sort_keys=True,
                          indent=self.indent, cls=self.json_encoder_cls)


class PPrintFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, options=None, indent=1):
        super(PPrintFormatter, self).__init__(fmt=fmt, datefmt=datefmt)

        self.indent = indent or options.get('indent') or 1

    def format(self, record):
        res_dict = record.__dict__.copy()
        message = record.getMessage()
        res_dict['message'] = message
        res = pprint.pformat(res_dict, indent=self.indent)
        return res

    def __repr__(self):
        buf = '%s(fmt="%s", options=%s, indent=%s)' % (self.__class__.__name__,
                                                       self._fmt, self.options,
                                                       self.indent)
        return buf


class DjangoDbSqlCeleryFilter(object):
    def filter(self, record):
        sql = getattr(record, 'sql', None)
        if not sql:
            return 1
        if 'djcelery_periodictask' in sql:
            return 0

        return 1


class DjangoDbSqlFormatter(logging.Formatter):
    '''pretty print django.db sql'''

    def __init__(self, fmt=None, datefmt=None, options=None):
        super(DjangoDbSqlFormatter, self).__init__(fmt=fmt, datefmt=datefmt)

        self.options = options or {'reindent': True,
                                   'keyword_case': 'upper'}

    def format(self, record):
        pretty_sql = sqlparse.format(record.sql,
                                     **self.options)

        record.sql = pretty_sql
        # import pprint
        # return '\n__dict__=%s\n' % pprint.pformat(record.__dict__)
        return super(DjangoDbSqlFormatter, self).format(record)

    def __repr__(self):
        buf = 'DjangoDbSqlFormatter(fmt="%s", options=%s)' % (self._fmt, self.options)
        return buf
