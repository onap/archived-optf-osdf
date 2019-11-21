# -------------------------------------------------------------------------
#   Copyright (c)  2019 Huawei Intellectual Property
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

from schematics.types import BaseType
from schematics.types.compound import ModelType, DictType

from .common import OSDFModel
from .nsCommon import RequestInfo


class NSTSelectionAPI(OSDFModel):
    """Request for NST Selection """
    requestInfo = ModelType(RequestInfo, required=True)
    serviceProfile = DictType(BaseType, required=True)
