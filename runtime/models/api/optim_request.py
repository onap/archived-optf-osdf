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

from schematics.types import BaseType, DictType, StringType, IntType
from schematics.types.compound import ModelType

from osdf.models.api.common import OSDFModel

"""
"""
class RequestInfo(OSDFModel):
    """Info for northbound request from client """
    transactionId = StringType(required=True)
    requestID = StringType(required=True)
    callbackUrl = StringType()
    sourceId = StringType(required=True)
    timeout = IntType()


class DataInfo(OSDFModel):
    """Optimization data info"""
    text = StringType()
    json = DictType(BaseType)


class OptimInfo(OSDFModel):
    """Optimizer request info details."""
    # ModelId from the database, if its not populated,
    # assume that solverModel will be populated.
    modelId = StringType()
    # type of solver (mzn, or-tools, etc.)
    solver = StringType()
    # Arguments for solver
    solverArgs = DictType(BaseType)
    # NOTE: a large blob string containing the model (which is not that
    # problematic since models are fairly small).
    modelContent = StringType()
    # Data Payload, input data for the solver
    optData = ModelType(DataInfo)


class OptimizationAPI(OSDFModel):
    """Request for Optimizer API (specific to optimization and additional metadata"""
    requestInfo = ModelType(RequestInfo, required=True)
    optimInfo = ModelType(OptimInfo, required=True)
