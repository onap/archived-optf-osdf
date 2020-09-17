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


__all__ = ["patch_all"]

from onaplogging.logWatchDog import patch_loggingYaml

from osdf.logging.oof_mdc_context import patch_logging_mdc


def patch_all(mdc=True, yaml=True):
    """monkey patch osdf logging to enable mdc

    """
    if mdc is True:
        patch_logging_mdc()

    if yaml is True:
        patch_loggingYaml()
