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

from osdf.adapters.conductor.demand import ModelMetaData, Candidates
from osdf.models.api.common import OSDFModel
from schematics.types import BaseType, StringType, URLType, IntType, BooleanType
from schematics.types.compound import ModelType, ListType, DictType


class RequestInfo(OSDFModel):
    """Info for northbound request from client such as SO"""
    transactionId = StringType(required=True)
    requestId = StringType(required=True)
    callbackUrl = URLType(required=True)
    callbackHeader = DictType(BaseType)
    sourceId = StringType(required=True)
    requestType = StringType(required=True)
    numSolutions = IntType()
    optimizers = ListType(StringType(required=True))
    timeout = IntType()


class LicenseModel(OSDFModel):
    entitlementPoolUUID = ListType(StringType(required=True))
    licenseKeyGroupUUID = ListType(StringType(required=True))


class LicenseDemands(OSDFModel):
    resourceModuleName = StringType(required=True)
    serviceResourceId = StringType(required=True)
    resourceModelInfo = ModelType(ModelMetaData, required=True)
    existingLicenses = ModelType(LicenseModel)


class LicenseInfo(OSDFModel):
    licenseDemands = ListType(ModelType(LicenseDemands))


class PlacementDemand(OSDFModel):
    resourceModuleName = StringType(required=True)
    serviceResourceId = StringType(required=True)
    tenantId = StringType()
    resourceModelInfo = ModelType(ModelMetaData, required=True)
    existingCandidates = ListType(ModelType(Candidates))
    excludedCandidates = ListType(ModelType(Candidates))
    requiredCandidates = ListType(ModelType(Candidates))


class ServiceInfo(OSDFModel):
    serviceInstanceId = StringType(required=True)
    modelInfo = ModelType(ModelMetaData, required=True)
    serviceName = StringType(required=True)


class SubscriberInfo(OSDFModel):
    """Details on the customer that subscribes to the VNFs"""
    globalSubscriberId = StringType(required=True)
    subscriberName = StringType()
    subscriberCommonSiteId = StringType()


class PlacementInfo(OSDFModel):
    """Information specific to placement optimization"""
    requestParameters = DictType(BaseType)
    placementDemands = ListType(ModelType(PlacementDemand), min_size=1)
    subscriberInfo = ModelType(SubscriberInfo)


class PlacementAPI(OSDFModel):
    """Request for placement optimization (specific to optimization and additional metadata"""
    requestInfo = ModelType(RequestInfo, required=True)
    placementInfo = ModelType(PlacementInfo, required=True)
    licenseInfo = ModelType(LicenseInfo)
    serviceInfo = ModelType(ServiceInfo, required=True)
