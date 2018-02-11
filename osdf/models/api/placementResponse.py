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

from .common import OSDFModel
from schematics.types import StringType
from schematics.types.compound import ModelType, ListType


# TODO: update osdf.models

class LicenseSolution(OSDFModel):
    serviceResourceId = StringType(required=True)
    resourceModuleName = StringType(required=True)
    entitlementPoolList = ListType(StringType(required=True))
    licenseKeyGroupList = ListType(StringType(required=True))


class AssignmentInfo(OSDFModel):
    variableName = StringType(required=True)
    variableValue = StringType(required=True)


class PlacementSolution(OSDFModel):
    serviceResourceId = StringType(required=True)
    resourceModuleName = StringType(required=True)
    inventoryType = StringType(required=True)
    serviceInstanceId = StringType()
    cloudRegionId = StringType()
    assignmentInfo = ListType(ModelType(AssignmentInfo))


class SolutionInfo(OSDFModel):
    placement = ListType(ModelType(PlacementSolution), min_size=1)
    license = ListType(ModelType(LicenseSolution), min_size=1)


class PlacementResponse(OSDFModel):
    transactionId = StringType(required=True)
    requestId = StringType(required=True)
    requestState = StringType(required=True)
    statusMessage = StringType(required=True)
    solutionInfo = ModelType(SolutionInfo)
