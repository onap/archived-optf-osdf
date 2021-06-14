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

from flask import request
from markupsafe import Markup

from osdf.apps.baseapp import app, run_app
from osdf.logging.osdf_logging import audit_log
from osdf.webapp.appcontroller import auth_basic
from runtime.model_api import create_model_data, retrieve_model_data, retrieve_all_models, delete_model_data
from runtime.models.api.model_request import OptimModelRequestAPI
from runtime.optim_engine import process_request


@app.route("/api/oof/optengine/v1", methods=["POST"])
@auth_basic.login_required
def opt_engine_rest_api():
    """Perform OptimEngine optimization after validating the request
    """
    request_json = request.get_json()
    return process_request(request_json)


@app.route("/api/oof/optmodel/v1", methods=["PUT", "POST"])
@auth_basic.login_required
def opt_model_create_rest_api():
    """Perform OptimEngine optimization after validating the request
    """
    request_json = request.get_json()
    OptimModelRequestAPI(request_json).validate()
    return create_model_data(request_json)


@app.route("/api/oof/optmodel/v1/<model_id>", methods=["GET"])
@auth_basic.login_required
def opt_get_model_rest_api(model_id):
    """Retrieve model data
    """
    model_id = Markup.escape(model_id)
    return retrieve_model_data(model_id)


@app.route("/api/oof/optmodel/v1", methods=["GET"])
@auth_basic.login_required
def opt_get_all_models_rest_api():
    """Retrieve all models data
    """
    return retrieve_all_models()


@app.route("/api/oof/optmodel/v1/<model_id>", methods=["DELETE"])
@auth_basic.login_required
def opt_delete_model_rest_api(model_id):
    """Perform OptimEngine optimization after validating the request
    """
    return delete_model_data(model_id)


@app.route("/api/oof/optengine/healthcheck/v1", methods=["GET"])
def do_health_check():
    """Simple health check"""
    audit_log.info("A OptimEngine health check v1 request is processed!")
    return "OK"


if __name__ == "__main__":
    run_app()
