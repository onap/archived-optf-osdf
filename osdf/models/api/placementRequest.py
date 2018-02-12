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
from schematics.types import BaseType, StringType, URLType, IntType
from schematics.types.compound import ModelType, ListType, DictType


class RequestInfo(OSDFModel):
    """Info for northbound request from client such as SO"""
    transactionId = StringType(required=True)
    requestId = StringType(required=True)
    callbackUrl = URLType(required=True)
    sourceId = StringType(required=True)
    optimizers = ListType(StringType(required=True))
    numSolutions = IntType()
    timeout = IntType()
    requestType = StringType()


class CandidateInfo(OSDFModel):
    """Preferred candidate for a resource (sent as part of a request from client)"""
    candidateType = StringType(required=True)
    candidates = ListType(StringType(required=True))


class ResourceModelInfo(OSDFModel):
    """Model information for a specific resource"""
    modelCustomizationId = StringType(required=True)
    modelInvariantId = StringType(required=True)
    modelName = StringType()
    modelVersion = StringType()
    modelVersionId = StringType()
    modelType = StringType()


class ExistingLicenseInfo(OSDFModel):
    entitlementPoolUUID = ListType(StringType())
    licenseKeyGroupUUID = ListType(StringType())


class LicenseDemand(OSDFModel):
    resourceInstanceType = StringType(required=True)
    serviceResourceId = StringType(required=True)
    resourceModuleName = StringType(required=True)
    resourceModelInfo = ModelType(ResourceModelInfo)
    existingLicense = ModelType(ExistingLicenseInfo)


class PlacementDemand(OSDFModel):
    resourceInstanceType = StringType(required=True)
    serviceResourceId = StringType(required=True)
    resourceModuleName = StringType(required=True)
    exclusionCandidateInfo = ListType(ModelType(CandidateInfo))
    requiredCandidateInfo = ListType(ModelType(CandidateInfo))
    resourceModelInfo = ModelType(ResourceModelInfo)
    tenantId = StringType(required=True)
    tenantName = StringType()

class ExistingPlacementInfo(OSDFModel):
    serviceInstanceId = StringType(required=True)


class DemandInfo(OSDFModel):
    """Requested resources (sent as part of a request from client)"""
    placementDemand = ListType(ModelType(PlacementDemand))
    licenseDemand = ListType(ModelType(LicenseDemand))


class SubscriberInfo(OSDFModel):
    """Details on the customer that subscribes to the VNFs"""
    globalSubscriberId = StringType(required=True)
    subscriberName = StringType()
    subscriberCommonSiteId = StringType()


class ServiceModelInfo(OSDFModel):
    """ASDC Service model information"""
    modelType = StringType(required=True)
    modelInvariantId = StringType(required=True)
    modelVersionId = StringType(required=True)
    modelName = StringType(required=True)
    modelVersion = StringType(required=True)


class PlacementInfo(OSDFModel):
    """Information specific to placement optimization"""
    serviceModelInfo = ModelType(ServiceModelInfo, required=True)
    subscriberInfo = ModelType(SubscriberInfo, required=True)
    demandInfo = ModelType(DemandInfo, required=True)
    requestParameters = DictType(BaseType)
    policyId = ListType(StringType())
    serviceInstanceId = StringType(required=True)
    existingPlacement = ModelType(ExistingPlacementInfo)


class PlacementAPI(OSDFModel):
    """Request for placement optimization (specific to optimization and additional metadata"""
    requestInfo = ModelType(RequestInfo, required=True)
    placementInfo = ModelType(PlacementInfo, required=True)
