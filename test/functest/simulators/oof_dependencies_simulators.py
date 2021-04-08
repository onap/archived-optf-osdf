# -------------------------------------------------------------------------
#   Copyright (c) 2018 AT&T Intellectual Property
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

"""
Simulators for dependencies of OSDF (e.g. HAS-API, Policy, SO-callback, etc.)
"""
import glob
import json
import os

from flask import Flask, jsonify, request

from osdf.utils.interfaces import json_from_file

app = Flask(__name__)


@app.route("/simulated/ERROR/<component>", methods=["GET", "POST"])
@app.route("/simulated/unhealthy/<component>", methods=["GET", "POST"])
def error_for_component(component):
    """Send an HTTP error for component"""
    return jsonify({"error": "{} error".format(component)}), 503


@app.route("/simulated/healthy/<component>", methods=["GET", "POST"])
def healthy_status_for_component(component):
    """Send a health-OK response for component"""
    return jsonify({"success": "Passed Health Check for Component {}".format(component)})


@app.route("/simulated/success/<component>", methods=["GET", "POST"])
def successful_call_for_component(component):
    """Send a message about successful call to component"""
    return jsonify({"success": "made a call to Component: {}".format(component)})


@app.route("/simulated/oof/has-api/<path:mainpath>", methods=["GET", "POST"])
def has_api_calls(mainpath):
    data, status = get_payload_for_simulated_component('has-api', mainpath)
    if not status:
        return jsonify(data)
    return jsonify(data), 503


def get_payload_for_simulated_component(component, mainpath):
    """
    Get the payload for the given path for the given component
    :param component: Component we are using (e.g. HAS-API, Policy, SO-callback, etc.)
    :param mainpath: path within the URL (e.g. /main/X1/y1/)
    :return: Content if file exists, or else 503 error
    """
    file_name = "{}/response-payloads/{}".format(component, mainpath)
    data = json_from_file(file_name)
    if not data:
        return {"Error": "Unable to read File {}".format(file_name)}, 503
    return data, None


@app.route("/simulated/policy/<sub_component>/getConfig", methods=["POST"])
def get_policies(sub_component):
    """
    Get all policies for this folder
    :param sub_component: The folder we are interested in (e.g. "pdp-has-vcpe-good", "pdp-has-vcpe-bad")
    :return: A list of policies as a json object (each element is one policy)
    """
    main_dir = "policy/response-payloads/" + sub_component
    files = glob.glob("{}/*.json".format(main_dir))
    list_json = []
    for x in files:
        list_json.append({
            "policyConfigMessage": "Config Retrieved! ",
            "policyConfigStatus": "CONFIG_RETRIEVED",
            "type": "JSON",
            "config": json.dumps(json_from_file(x)),
            "policyName": os.path.basename(x),
            "policyType": "MicroService",
            "policyVersion": "1"
        })
    return jsonify(list_json)


@app.route("/simulated/policy/pdpx/decision/v1", methods=["POST"])
def get_pdx_policies():
    """
    get the pdpx policy
    """
    return jsonify(json_from_file("policy/response-payloads/policy_response.json"))


@app.route("/simulated/configdb/getCellList/<network_id>/<ts>", methods=["GET"])
def get_cell_list(network_id, ts):
    data, status = get_payload_for_simulated_component('configdb',
                                                       'getCellList-' + network_id + '.json')
    if not status:
        return jsonify(data)
    return jsonify(data), 503


@app.route("/simulated/configdb/getNbrList/<cell_id>/<ts>", methods=["GET"])
def get_nbr_list(cell_id, ts):
    data, status = get_payload_for_simulated_component('configdb', 'getNbrList-' + cell_id + '.json')
    if not status:
        return jsonify(data)
    return jsonify(data), 503


@app.route("/simulated/aai/v23/dsl", methods=["PUT"])
def dsl_query():

    nsi_query = {"dsl": "service-instance*('service-instance-id','9629e36c-a3d9-4aed-8368-f72b8be1cd34') > "
                        "service-instance*('service-role','e2eserviceprofile-service')"}

    nssi_query = {"dsl": "service-instance*('service-instance-id','9629e36c-a3d9-4aed-8368-f72b8be1cd34') > "
                         "service-instance*('service-role','nsi')"}

    nsi_with_sp_query = {"dsl": "service-instance*('service-instance-id','9629e36c-a3d9-4aed-8368-f72b8be1cd34') > "
                                "service-instance*('service-role','e2eserviceprofile-service')("
                                "'service-instance-id',"
                                "'660ca85c-1a0f-4521-a559-65f23e794699660ca85c-1a0f-4521-a559-65f23e794699')"}

    nssi_with_nsi_query = {"dsl": "service-instance*('service-instance-id','9629e36c-a3d9-4aed-8368-f72b8be1cd34') > "
                                  "service-instance*('service-role','nsi')('service-instance-id',"
                                  "'660ca85c-1a0f-4521-a559-65f23e794699')"}

    queries = {
        "nsi": nsi_query,
        "nssi_query": nssi_query,
        "nsi_with_sp": nsi_with_sp_query,
        "nssi_with_nsi": nssi_with_nsi_query
    }

    count = {
        "nsi": 1,
        "nssi_query": 1,
        "nsi_with_sp": 2,
        "nssi_with_nsi": 2
    }

    request_body = request.get_json()
    service_count = 0
    for query_type, query in queries.items():
        if request_body == query:
            service_count = count[query_type]
    return {'results': [{'service-instance': service_count}]}


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
