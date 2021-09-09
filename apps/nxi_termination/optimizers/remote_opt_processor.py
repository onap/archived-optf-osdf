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

from jinja2 import Template

from apps.nxi_termination.optimizers.response_processor import get_nxi_termination_response
from osdf.adapters.aai.fetch_aai_data import AAIException
from osdf.adapters.aai.fetch_aai_data import execute_dsl_query
from osdf.adapters.aai.fetch_aai_data import get_aai_data
from osdf.logging.osdf_logging import debug_log


def process_nxi_termination_opt(request_json, osdf_config):
    """Process the nxi Termination request from API layer

           :param request_json: api request
           :param osdf_config: configuration specific to OSDF app
           :return: response as a success,failure
    """

    request_type = request_json["type"]
    request_info = request_json.get("requestInfo", {})
    addtnl_args = request_info.get("addtnlArgs", {})
    query_templates = osdf_config.core["nxi_termination"]["query_templates"]

    inputs = {
        "instance_id": request_json["NxIId"]
    }

    try:
        if request_type == "NSSI":
            templates = query_templates["nssi"]
            for template in templates:
                resource_count = get_resource_count(template, inputs, osdf_config)
                if resource_count == -1:
                    continue
                elif resource_count > 1 or (resource_count == 1 and not addtnl_args.get("serviceInstanceId")):
                    terminate_response = False
                elif resource_count == 0:
                    terminate_response = True
                elif resource_count == 1 and addtnl_args.get("serviceInstanceId"):
                    new_template = template + "('service-instance-id','{}')".format(addtnl_args["serviceInstanceId"])
                    terminate_response = get_resource_count(new_template, inputs, osdf_config) == 1
                return set_response("success", "", request_info, terminate_response)

        if request_type == "NSI":
            allotted_resources = get_allotted_resources(request_json, osdf_config)
            resource_count = len(allotted_resources)
            if resource_count == 1 and addtnl_args.get("serviceInstanceId"):
                debug_log.debug("resource count {}".format(resource_count))
                terminate_response = False
                properties = allotted_resources[0]["relationship-data"]
                for property in properties:
                    if property["relationship-key"] == "service-instance.service-instance-id" \
                        and property["relationship-value"] == addtnl_args.get("serviceInstanceId"):
                        terminate_response = True
            elif resource_count > 1 or (resource_count == 1 and not addtnl_args.get("serviceInstanceId")):
                terminate_response = False
            elif resource_count == 0:
                terminate_response = True

        return set_response("success", "", request_info, terminate_response)
    except AAIException as e:
        reason = str(e)
        return set_response("failure", reason, request_info)

    except Exception as e:
        reason = "{} Exception Occurred while processing".format(str(e))
        return set_response("failure", reason, request_info)


def set_response(status, reason, request_info, terminate_response=None):
    res = dict()
    res["requestStatus"] = status
    res["terminateResponse"] = terminate_response
    res["reason"] = reason
    return get_nxi_termination_response(request_info, res)


def get_resource_count(query_template, inputs, osdf_config):
    query = Template(query_template).render(inputs)
    dsl_response = execute_dsl_query(query, "count", osdf_config)
    debug_log.debug("dsl_response {}".format(dsl_response))
    # the dsl query with format "count" includes the original service-instance, hence reducing one from the result
    count = dsl_response["results"][0]
    return count.get("service-instance", 0) - 1


def get_allotted_resources(request_json, osdf_config):
    response = get_aai_data(request_json, osdf_config)
    rel_list = response["relationship-list"]["relationship"]
    return [rel for rel in rel_list if rel["related-to"] == "allotted-resource"]
