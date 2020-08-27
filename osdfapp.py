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

"""
OSDF Manager Main Flask Application
"""

import json

from threading import Thread  # for scaling up, may need celery with RabbitMQ or redis

from flask import request, g

from osdf.apps.baseapp import app, run_app
from apps.nst.models.api.nstSelectionRequest import NSTSelectionAPI
from apps.pci.models.api.pciOptimizationRequest import PCIOptimizationAPI
from apps.nst.optimizers.nst_select_processor import process_nst_selection
from apps.pci.optimizers.pci_opt_processor import process_pci_optimation
from apps.placement.models.api.placementRequest import PlacementAPI
from apps.placement.optimizers.conductor.remote_opt_processor import process_placement_opt
from apps.route.optimizers.inter_domain_route_opt import InterDomainRouteOpt
from apps.route.optimizers.simple_route_opt import RouteOpt
from apps.slice_selection.models.api.nsi_selection_request import NSISelectionAPI
from apps.slice_selection.optimizers.conductor.remote_opt_processor import process_nsi_selection_opt
from osdf.adapters.policy.interface import get_policies
from osdf.adapters.policy.interface import upload_policy_models
from osdf.config.base import osdf_config
from osdf.logging.osdf_logging import MH, audit_log
from osdf.operation.responses import osdf_response_for_request_accept as req_accept
from osdf.utils import api_data_utils
from osdf.webapp.appcontroller import auth_basic


@app.route("/api/oof/v1/healthcheck", methods=["GET"])
def do_osdf_health_check():
    """Simple health check"""
    audit_log.info("A health check request is processed!")
    return "OK"


@app.route("/api/oof/loadmodels/v1", methods=["GET"])
def do_osdf_load_policies():
    audit_log.info("Uploading policy models")
    """Upload policy models"""
    response = upload_policy_models()
    audit_log.info(response)
    return "OK"


@app.route("/api/oof/v1/placement", methods=["POST"])
@auth_basic.login_required
def do_placement_opt():
    return placement_rest_api()


@app.route("/api/oof/placement/v1", methods=["POST"])
@auth_basic.login_required
def do_placement_opt_common_versioning():
    return placement_rest_api()


def placement_rest_api():
    """Perform placement optimization after validating the request and fetching policies
    Make a call to the call-back URL with the output of the placement request.
    Note: Call to Conductor for placement optimization may have redirects, so account for them
    """
    request_json = request.get_json()
    req_id = request_json['requestInfo']['requestId']
    g.request_id = req_id
    audit_log.info(MH.received_request(request.url, request.remote_addr, json.dumps(request_json)))
    api_version_info = api_data_utils.retrieve_version_info(request, req_id)
    PlacementAPI(request_json).validate()
    policies = get_policies(request_json, "placement")
    audit_log.info(MH.new_worker_thread(req_id, "[for placement]"))
    t = Thread(target=process_placement_opt, args=(request_json, policies, osdf_config))
    t.start()
    audit_log.info(MH.accepted_valid_request(req_id, request))
    return req_accept(request_id=req_id,
                      transaction_id=request_json['requestInfo']['transactionId'],
                      version_info=api_version_info, request_status="accepted", status_message="")


@app.route("/api/oof/route/v1", methods=["POST"])
def do_route_calc():
    """
    Perform the basic route calculations and returnn the vpn-bindings
    """
    request_json = request.get_json()
    audit_log.info("Calculate Route request received!")
    response = RouteOpt().get_route(request_json, osdf_config)
    return response

@app.route("/api/oof/mdons/route/v1", methods=["POST"])
def do_mdons_route_calc():
    """
    Perform the inter domain route calculation
    """
    request_json = request.get_json()
    audit_log.info("Inter Domain Calculation  Route request received!")
    response = InterDomainRouteOpt().get_route(request_json, osdf_config)
    return response

@app.route("/api/oof/v1/selection/nst", methods=["POST"])
def do_nst_selection():
    request_json = request.get_json()
    req_id = request_json['requestInfo']['requestId']
    NSTSelectionAPI(request_json).validate()
    response = process_nst_selection(request_json, osdf_config)
    return response

@app.route("/api/oof/v1/pci", methods=["POST"])
@app.route("/api/oof/pci/v1", methods=["POST"])
@auth_basic.login_required
def do_pci_optimization():
    request_json = request.get_json()
    audit_log.info('request json obtained==>')
    audit_log.info(request_json)

    req_id = request_json['requestInfo']['requestId']
    audit_log.info('requestID obtained==>')
    audit_log.info(req_id)

    g.request_id = req_id
    audit_log.info(MH.received_request(request.url, request.remote_addr, json.dumps(request_json)))
    PCIOptimizationAPI(request_json).validate()
    # disable policy retrieval
    # policies = get_policies(request_json, "pciopt")
    audit_log.info(MH.new_worker_thread(req_id, "[for pciopt]"))
    t = Thread(target=process_pci_optimation, args=(request_json, osdf_config, None))
    t.start()
    audit_log.info(MH.accepted_valid_request(req_id, request))
    audit_log.info('reached upto return')
    return req_accept(request_id=req_id,
                      transaction_id=request_json['requestInfo']['transactionId'],
                      request_status="accepted", status_message="")


@app.route("/api/oof/selection/nsi/v1", methods=["POST"])
def do_nsi_selection():
    request_json = request.get_json()
    req_id = request_json['requestInfo']['requestId']
    g.request_id = req_id
    audit_log.info(MH.received_request(request.url, request.remote_addr, json.dumps(request_json)))
    NSISelectionAPI(request_json).validate()
    audit_log.info(MH.new_worker_thread(req_id, "[for NSI selection]"))
    t = Thread(target=process_nsi_selection_opt, args=(request_json, osdf_config))
    t.start()
    return req_accept(request_id=req_id,
                      transaction_id=request_json['requestInfo']['transactionId'],
                      request_status="accepted", status_message="")


@app.route("/api/oof/selection/nssi/v1", methods=["POST"])
def do_nssi_selection():
    request_json = request.get_json()
    req_id = request_json['requestInfo']['requestId']
    g.request_id = req_id
    audit_log.info(MH.received_request(request.url, request.remote_addr, json.dumps(request_json)))
    NSSISelectionAPI(request_json).validate()
    audit_log.info(MH.new_worker_thread(req_id, "[for NSSI selection]"))
    t = Thread(target=process_nsi_selection_opt, args=(request_json, osdf_config))
    t.start()
    return req_accept(request_id=req_id,
                      transaction_id=request_json['requestInfo']['transactionId'],
                      request_status="accepted", status_message="")


if __name__ == "__main__":
    run_app()
