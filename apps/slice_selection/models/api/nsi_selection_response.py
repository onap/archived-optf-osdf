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
from schematics.types import BaseType, StringType, BooleanType
from schematics.types.compound import ModelType, ListType, DictType


# TODO: update osdf.models
class SharedNSISolution(OSDFModel):
    """Represents the shared NSI Solution object"""
    invariantUUID = StringType(required=True)
    UUID = StringType(required=True)
    NSIName = StringType(required=True)
    NSIId = StringType(required=True)
    matchLevel = StringType(required=True)


class NewNSISolution(OSDFModel):
    """Represents the New NSI Solution object containing tuple of slice profiles"""
    sliceProfiles = ListType(DictType(BaseType), required=True)
    matchLevel = StringType(required=True)


class NSISolution(OSDFModel):
    """Represents the NSI Solution object"""
    """This solution object contains either sharedNSISolution or newNSISolution"""
    existingNSI = BooleanType(required=True)
    sharedNSISolution = ModelType(SharedNSISolution)
    newNSISolution = ModelType(NewNSISolution)


class NSISelectionResponse(OSDFModel):
    """Response sent to NSMF(SO)"""
    transactionId = StringType(required=True)
    requestId = StringType(required=True)
    requestStatus = StringType(required=True)
    solutions = ListType(ModelType(NSISolution), required=True)
    statusMessage = StringType()
