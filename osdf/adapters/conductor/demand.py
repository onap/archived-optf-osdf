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
from schematics.types import StringType
from schematics.types.compound import ModelType, ListType


class ModelMetaData(OSDFModel):
    """Model information for a specific resource"""
    modelInvariantId = StringType(required=True)
    modelVersionId = StringType(required=True)
    modelName = StringType()
    modelType = StringType()
    modelVersion = StringType()
    modelCustomizationName = StringType()


class Candidates(OSDFModel):
    """Preferred candidate for a resource (sent as part of a request from client)"""
    identifierType = StringType(required=True)
    identifiers = ListType(StringType(required=True))
    cloudOwner = StringType()


class Demand(OSDFModel):
    resourceModuleName = StringType(required=True)
    serviceResourceId = StringType()
    tenantId = StringType()
    resourceModelInfo = ModelType(ModelMetaData, required=True)
    existingCandidates = ListType(ModelType(Candidates))
    excludedCandidates = ListType(ModelType(Candidates))
    requiredCandidates = ListType(ModelType(Candidates))
