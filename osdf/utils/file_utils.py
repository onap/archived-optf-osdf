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

#  File related utilities

import os
from shutil import rmtree

from osdf.logging.osdf_logging import debug_log


def delete_file_folder(p):
    if not p:
        return
    debug_log.debug('Deleting folder/file {}'.format(p))
    if os.path.isfile(p):
        os.remove(p)
    else:
        rmtree(p, ignore_errors=True)
