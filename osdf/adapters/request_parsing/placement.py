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

import copy
import json
from osdf.utils.programming_utils import list_flatten, dot_notation


def json_path_after_expansion(req_json, reference):
    """
    Get the child node(s) from the dot-notation [reference] and parent [req_json].
    For placement and other requests, there are encoded JSONs inside the request or policy,
    so we need to expand it and then do a search over the parent plus expanded JSON.
    """
    req_json_copy = copy.deepcopy(req_json)  # since we expand the JSON in place, we work on a copy
    req_json_copy['placementInfo']['orderInfo'] = json.loads(req_json_copy['placementInfo']['orderInfo'])
    info = dot_notation(req_json_copy, reference)
    return list_flatten(info) if isinstance(info, list) else info
