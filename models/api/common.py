# -------------------------------------------------------------------------
#   Copyright (c) 2015-2017 AT&T Intellectual Property
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

import datetime
from pprint import pformat

from dateutil.parser import parse
from schematics.exceptions import ConversionError
from schematics.models import Model
from schematics.types import DateTimeType


class OSDFModel(Model):
    """Extends generic model with a couple of extra methods"""
    def __str__(self):
        """Return values of object's attributes -- excluding hidden or callable ones"""
        def _str_format(x):
            """Coerce as string for some special objects"""
            return str(x) if isinstance(x, datetime.datetime) else x

        z1 = dict((x, getattr(self, x)) for x in dir(self)
                  if not x.startswith("_") and not callable(getattr(self, x)))
        z1 = dict((x, _str_format(y)) for x, y in z1.items())
        return pformat(z1, depth=4, indent=2, width=1000)

    def __repr__(self):
        """Return values of object's attributes -- excluding hidden or callable ones"""
        return self.__str__()


class CustomISODateType(DateTimeType):
    """Schematics doesn't support full ISO, so we use custom one"""
    def to_native(self, value, context=None):
        if isinstance(value, datetime.datetime):
            return value
        try:
            return parse(value)
        except:
            raise ConversionError(u'Invalid timestamp {}'.format(value))
