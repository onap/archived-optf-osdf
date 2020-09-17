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

import time

from onaplogging.colorFormatter import RESET
from onaplogging.mdcformatter import MDCFormatter


class OOFMDCFormatter(MDCFormatter):
    """ONAP MDC formatter

    """

    def __init__(self, fmt=None, mdcfmt=None,
                 datefmt=None, colorfmt=None, style="%"):
        super().__init__(fmt, mdcfmt, datefmt, colorfmt, style)
        self.converter = time.gmtime

    def _replaceStr(self, keys):
        """

        """
        fmt = self._mdcFmt
        for i in keys:
            fmt = fmt.replace(i, i)

        return fmt

    def format(self, record):
        """Removing the color format end of line character.

        """
        return super(OOFMDCFormatter, self).format(record).replace(RESET, '')
