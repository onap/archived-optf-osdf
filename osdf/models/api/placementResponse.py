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
from schematics.types import BaseType, StringType
from schematics.types.compound import ModelType, ListType, DictType


# TODO: update osdf.models

class LicenseSolution(OSDFModel):
    serviceResourceId = StringType(required=True)
    resourceModuleName = StringType(required=True)
    entitlementPoolUUID = ListType(StringType(required=True))
    licenseKeyGroupUUID = ListType(StringType(required=True))
    entitlementPoolInvariantUUID = ListType(StringType(required=True))
    licenseKeyGroupInvariantUUID = ListType(StringType(required=True))


class Candidates(OSDFModel):
    """Preferred candidate for a resource (sent as part of a request from client)"""
    identifierType = StringType(required=True)
    identifiers = ListType(StringType(required=True))
    cloudOwner = StringType()


class AssignmentInfo(OSDFModel):
    key = StringType(required=True)
    value = BaseType(required=True)


class PlacementSolution(OSDFModel):
    serviceResourceId = StringType(required=True)
    resourceModuleName = StringType(required=True)
    solution = ModelType(Candidates, required=True)
    assignmentInfo = ListType(ModelType(AssignmentInfo))


class Solution(OSDFModel):
    placementSolutions = ListType(ListType(ModelType(PlacementSolution), min_size=1))
    licenseSolutions = ListType(ModelType(LicenseSolution), min_size=1)


class PlacementResponse(OSDFModel):
    transactionId = StringType(required=True)
    requestId = StringType(required=True)
    requestStatus = StringType(required=True)
    statusMessage = StringType()
    solutions = ModelType(Solution, required=True)
