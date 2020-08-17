# -------------------------------------------------------------------------
#   Copyright (C) 2020 Wipro Limited.
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
from schematics.types import BaseType, StringType, URLType, IntType
from schematics.types.compound import ModelType, DictType

from apps.slice_selection.models.api.nsi_selection_request import NxTInfo


class RequestInfo(OSDFModel):
    """Info for northbound request from client such as SO"""
    transactionId = StringType(required=True)
    requestId = StringType(required=True)
    callbackUrl = URLType(required=True)
    sourceId = StringType(required=True)
    callbackHeader = DictType(BaseType)
    timeout = IntType()
    numSolutions = IntType()
    addtnlArgs = DictType(BaseType)


class NSSISelectionAPI(OSDFModel):
    """Request for NSSI selection (specific to optimization and additional metadata"""
    requestInfo = ModelType(RequestInfo, required=True)
    NSSTInfo = ModelType(NxTInfo, required=True)
    sliceProfile = DictType(BaseType, required=True)
