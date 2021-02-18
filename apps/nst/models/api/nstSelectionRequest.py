# -------------------------------------------------------------------------
#   Copyright (c) 2020 Huawei Intellectual Property
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

from osdf.models.api.common import OSDFModel
from schematics.types import BaseType
from schematics.types.compound import DictType
from schematics.types.compound import ModelType
from schematics.types import IntType
from schematics.types import StringType
from schematics.types import URLType


class RequestInfo(OSDFModel):
    """Info for northbound request from client such as SO"""

    transactionId = StringType(required=True)
    requestId = StringType(required=True)
    callbackUrl = URLType(required=True)
    callbackHeader = DictType(BaseType)
    sourceId = StringType(required=True)
    timeout = IntType()
    numSolutions = IntType()


class NSTSelectionAPI(OSDFModel):
    """Request for NST selection """

    requestInfo = ModelType(RequestInfo, required=True)
    serviceProfile = DictType(BaseType)
