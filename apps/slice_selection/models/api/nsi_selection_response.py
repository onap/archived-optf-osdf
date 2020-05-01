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
from schematics.types import BaseType, StringType
from schematics.types.compound import ModelType, ListType, DictType


# TODO: update osdf.models
class NSSI(OSDFModel):
    NSSIId = StringType(required=True)
    NSSIName = StringType(required=True)
    UUID = StringType(required=True)
    invariantUUID = StringType(required=True)
    sliceProfile = ListType(DictType(BaseType))


class SharedNSISolution(OSDFModel):
    invariantUUID = StringType(required=True)
    UUID = StringType(required=True)
    NSIName = StringType(required=True)
    NSIId = StringType(required=True)
    matchLevel = StringType(required=True)
    NSSIs = ListType(ModelType(NSSI))


class NSSTInfo(OSDFModel):
    invariantUUID = StringType(required=True)
    UUID = StringType(required=True)
    NSSTName = StringType(required=True)


class NSSIInfo(OSDFModel):
    NSSIName = StringType(required=True)
    NSSIId = StringType(required=True)
    matchLevel = StringType(required=True)


class NSSISolution(OSDFModel):
    sliceProfile = DictType(BaseType)
    NSSTInfo = ModelType(NSSTInfo, required=True)
    NSSISolution = ModelType(NSSIInfo, required=True)


class NSTInfo(OSDFModel):
    invariantUUID = StringType(required=True)
    UUID = StringType(required=True)
    NSTName = StringType(required=True)


class NewNSISolution(OSDFModel):
    matchLevel = StringType(required=True)
    NSTInfo = ModelType(NSTInfo, required=True)
    NSSISolutions = ListType(ModelType(NSSISolution))


class Solution(OSDFModel):
    sharedNSISolutions = ListType(ModelType(SharedNSISolution))
    newNSISolutions = ListType(ModelType(NewNSISolution))


class NSISelectionResponse(OSDFModel):
    transactionId = StringType(required=True)
    requestId = StringType(required=True)
    requestStatus = StringType(required=True)
    statusMessage = StringType()
    solutions = ModelType(Solution, required=True)
