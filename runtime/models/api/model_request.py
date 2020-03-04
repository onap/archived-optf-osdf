# -------------------------------------------------------------------------
#   Copyright (c) 2020 AT&T Intellectual Property
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

from schematics.types import StringType
from schematics.types.compound import ModelType

from osdf.models.api.common import OSDFModel


class RequestInfo(OSDFModel):
    """Info for northbound request from client such as PCI-mS Handler"""
    transactionId = StringType(required=True)
    requestID = StringType(required=True)
    sourceId = StringType(required=True)


class OptimModelInfo(OSDFModel):
    """Optimizer request info details."""
    # ModelId from the database
    modelId = StringType()
    # type of solver (mzn, or-tools, etc.)
    solver = StringType(required=True)
    # Description of the model
    description = StringType()
    # a large blob string containing the model (which is not that
    # problematic since models are fairly small).
    modelContent = StringType()


class OptimModelRequestAPI(OSDFModel):
    """Request for Optimizer API (specific to optimization and additional metadata"""
    requestInfo = ModelType(RequestInfo, required=True)
    modelInfo = ModelType(OptimModelInfo, required=True)
