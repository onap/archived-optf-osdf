# -------------------------------------------------------------------------
#   Copyright (c) 2020 AT&T Intellectual Property
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# -------------------------------------------------------------------------
#

import logging
import re
import sys

from onaplogging.marker import MARKER_TAG
from onaplogging.marker import Marker
from onaplogging.mdcContext import MDC
from onaplogging.mdcContext import _replace_func_name
from onaplogging.mdcContext import fetchkeys
from onaplogging.mdcContext import findCaller as fc

from osdf.utils.mdc_utils import set_error_details


def findCaller(self, stack_info=False, stacklevel=1):
    """replacing onaplogging.mdcContext with this method to work with py3.8

    """
    return fc(stack_info)


def mdc_mapper():
    """Convert the MDC dict into comma separated, name=value string

    :return: string format
    """
    return ','.join(f'{k}={v}' for (k, v) in MDC.result().items() if k not in ['customField2'])


@fetchkeys
def info(self, msg, *args, **kwargs):
    """
    Wrapper method for log.info is called
    """
    if self.isEnabledFor(logging.INFO):
        MDC.put('customField2', mdc_mapper())
        self._log(logging.INFO, no_sep(msg), args, **kwargs)


@fetchkeys
def debug(self, msg, *args, **kwargs):
    """
    Wrapper method for log.debug is called
    msg: log message
    args: logging args
    kwargs: all the optional args
    """
    if self.isEnabledFor(logging.DEBUG):
        self._log(logging.DEBUG, no_sep(msg), args, **kwargs)


@fetchkeys
def warning(self, msg, *args, **kwargs):
    """
    Wrapper method for log.warning is called
    msg: log message
    args: logging args
    kwargs: all the optional args
    """
    if self.isEnabledFor(logging.WARNING):
        self._log(logging.WARNING, no_sep(msg), args, **kwargs)


@fetchkeys
def exception(self, msg, *args, **kwargs):
    """Wrapper method for log.exception is called

    msg: log message
    args: logging args
    kwargs: all the optional args
    """
    kwargs['exc_info'] = 1
    self.error(no_sep(msg), *args, **kwargs)


@fetchkeys
def critical(self, msg, *args, **kwargs):
    """Wrapper method for log.critical

    msg: log message
    args: logging args
    kwargs: all the optional args
    """
    if self.isEnabledFor(logging.CRITICAL):
        self._log(logging.CRITICAL, no_sep(msg), args, **kwargs)


@fetchkeys
def error(self, msg, *args, **kwargs):
    """Wrapper method for log.error is called

    msg: log message
    args: logging args
    kwargs: all the optional args
    """
    if self.isEnabledFor(logging.ERROR):
        if not MDC.get('errorCode'):
            set_error_details(400, 'Internal Error')
        MDC.put('customField2', mdc_mapper())
        self._log(logging.ERROR, no_sep(msg), args, **kwargs)


@fetchkeys
def log(self, level, msg, *args, **kwargs):
    """Wrapper method for log.log is called

    msg: log message
    args: logging args
    kwargs: all the optional args
    """
    if not isinstance(level, int):
        if logging.raiseExceptions:
            raise TypeError("level must be an integer")
        else:
            return

    if self.isEnabledFor(level):
        self._log(level, no_sep(msg), args, **kwargs)


def handle(self, record):
    """Wrapper method for log.handle is called

    """
    c_marker = getattr(self, MARKER_TAG, None)

    if isinstance(c_marker, Marker):
        setattr(record, MARKER_TAG, c_marker)

    if (not self.disabled) and self.filter(record):
        self.callHandlers(record)


def no_sep(message):
    """This method will remove newline, | from the message

    """
    if message is None:
        return ''
    return re.sub(r'[\|\n]', ' ', str(message))


def patch_logging_mdc():
    """The patch to add MDC ability in logging Record instance at runtime

    """
    local_module = sys.modules[__name__]
    for attr in dir(logging.Logger):
        if attr in _replace_func_name:
            new_func = getattr(local_module, attr, None)
            if new_func:
                setattr(logging.Logger, attr, new_func)
