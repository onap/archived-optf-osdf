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
from schematics.types import BaseType
from schematics.types import BooleanType
from schematics.types.compound import DictType
from schematics.types.compound import ListType
from schematics.types.compound import ModelType
from schematics.types import IntType
from schematics.types import StringType
from schematics.types import URLType


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


class NxTInfo(OSDFModel):
    """Information about NST/NSST model"""
    invariantUUID = StringType(required=True)
    UUID = StringType(required=True)
    name = StringType(required=True)


class SubnetCapability(OSDFModel):
    """Subnet capability of every subnet"""
    domainType = StringType(required=True)
    capabilityDetails = DictType(BaseType, required=True)


class NSISelectionAPI(OSDFModel):
    """Request for nsi selection (specific to optimization and additional metadata"""
    requestInfo = ModelType(RequestInfo, required=True)
    NSTInfo = ModelType(NxTInfo, required=True)
    NSSTInfo = ListType(ModelType(NxTInfo), required=False)
    serviceProfile = DictType(BaseType, required=True)
    subnetCapabilities = ListType(ModelType(SubnetCapability), required=True)
    preferReuse = BooleanType()
