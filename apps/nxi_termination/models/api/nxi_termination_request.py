
from osdf.models.api.common import OSDFModel
from schematics.types import BaseType
from schematics.types.compound import DictType
from schematics.types.compound import ModelType
from schematics.types import IntType
from schematics.types import StringType
from schematics.types import URLType


class RequestInfo(OSDFModel):
    """Info for northbound request from client such as SO"""
    transactionId = StringType(required=True)
    requestId = StringType(required=True)
    callbackUrl = URLType(required=True)
    callbackHeader = DictType(BaseType)
    sourceId = StringType(required=True)
    timeout = IntType()
    addtnlArgs = DictType(BaseType)


class NxiTerminationApi(OSDFModel):
    """Request for nxi termination (specific to optimization and additional metadata"""
    requestInfo = ModelType(RequestInfo, required=True)
    type = StringType(required=True)
    NxIId = StringType(required=True)
    UUID = StringType()
    invariantUUID = StringType()
