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

import json
import traceback

import mysql.connector
from flask import g, Flask, Response

from osdf.config.base import osdf_config
from osdf.logging.osdf_logging import debug_log, error_log
from osdf.operation.exceptions import BusinessException
from osdf.utils.data_conversion import decode_data


def init_db():
    if is_db_enabled():
        get_db()


def get_db():
    """Opens a new database connection if there is none yet for the
        current application context. 
    """
    if not hasattr(g, 'pg'):
        properties = osdf_config['deployment']
        host, db_port, db = properties["osdfDatabaseHost"], properties["osdfDatabasePort"], \
                            properties.get("osdfDatabaseSchema")
        user, password = properties["osdfDatabaseUsername"], properties["osdfDatabasePassword"]
        g.pg = mysql.connector.connect(host=host, port=db_port, user=user, password=password, database=db)
    return g.pg


def close_db():
    """Closes the database again at the end of the request."""
    if hasattr(g, 'pg'):
        g.pg.close()


app = Flask(__name__)


def create_model_data(model_api):
    with app.app_context():
        try:
            model_info = model_api['modelInfo']
            model_id = model_info['modelId']
            debug_log.debug(
                "persisting model_api {}".format(model_id))
            connection = get_db()
            cursor = connection.cursor(buffered=True)
            query = "SELECT model_id FROM optim_model_data WHERE model_id = %s"
            values = (model_id,)
            cursor.execute(query, values)
            if cursor.fetchone() is None:
                query = "INSERT INTO optim_model_data (model_id, model_content, description, solver_type) VALUES " \
                        "(%s, %s, %s, %s)"
                values = (model_id, model_info['modelContent'], model_info.get('description'), model_info['solver'])
                cursor.execute(query, values)
                g.pg.commit()

                debug_log.debug("A record successfully inserted for request_id: {}".format(model_id))
                return retrieve_model_data(model_id)
                close_db()
            else:
                query = "UPDATE optim_model_data SET model_content = %s, description = %s, solver_type = %s where " \
                        "model_id = %s "
                values = (model_info['modelContent'], model_info.get('description'), model_info['solver'], model_id)
                cursor.execute(query, values)
                g.pg.commit()

                return retrieve_model_data(model_id)
                close_db()
        except Exception as err:
            error_log.error("error for request_id: {} - {}".format(model_id, traceback.format_exc()))
            close_db()
            raise BusinessException(err)


def retrieve_model_data(model_id):
    status, resp_data = get_model_data(model_id)

    if status == 200:
        resp = json.dumps(build_model_dict(resp_data))
        return build_response(resp, status)
    else:
        resp = json.dumps({
            'modelId': model_id,
            'statusMessage': "Error retrieving the model data for model {} due to {}".format(model_id, resp_data)
        })
        return build_response(resp, status)


def build_model_dict(resp_data, content_needed=True):
    resp = {'modelId': resp_data[0], 'description': resp_data[2] if resp_data[2] else '',
            'solver': resp_data[3]}
    if content_needed:
        resp.update({'modelContent': decode_data(resp_data[1])})
    return resp


def build_response(resp, status):
    response = Response(resp, content_type='application/json; charset=utf-8')
    response.headers.add('content-length', len(resp))
    response.status_code = status
    return response


def delete_model_data(model_id):
    with app.app_context():
        try:
            debug_log.debug("deleting model data given model_id = {}".format(model_id))
            d = dict();
            connection = get_db()
            cursor = connection.cursor(buffered=True)
            query = "delete from optim_model_data WHERE model_id = %s"
            values = (model_id,)
            cursor.execute(query, values)
            g.pg.commit()
            close_db()
            resp = {
                "statusMessage": "model data for modelId {} deleted".format(model_id)
            }
            return build_response(json.dumps(resp), 200)
        except Exception as err:
            error_log.error("error deleting model_id: {} - {}".format(model_id, traceback.format_exc()))
            close_db()
            raise BusinessException(err)


def get_model_data(model_id):
    with app.app_context():
        try:
            debug_log.debug("getting model data given model_id = {}".format(model_id))
            d = dict();
            connection = get_db()
            cursor = connection.cursor(buffered=True)
            query = "SELECT model_id, model_content, description, solver_type  FROM optim_model_data WHERE model_id = %s"
            values = (model_id,)
            cursor.execute(query, values)
            if cursor is None:
                return 400, "FAILED"
            else:
                rows = cursor.fetchone()
                if rows is not None:
                    index = 0
                    for row in rows:
                        d[index] = row
                        index = index + 1
                    return 200, d
                else:
                    close_db()
                    return 500, "NOT_FOUND"
        except Exception:
            error_log.error("error for request_id: {} - {}".format(model_id, traceback.format_exc()))
            close_db()
            return 500, "FAILED"


def retrieve_all_models():
    status, resp_data = get_all_models()
    model_list = []
    if status == 200:
        for r in resp_data:
            model_list.append(build_model_dict(r, False))
        resp = json.dumps(model_list)
        return build_response(resp, status)

    else:
        resp = json.dumps({
            'statusMessage': "Error retrieving all the model data due to {}".format(resp_data)
        })
        return build_response(resp, status)


def get_all_models():
    with app.app_context():
        try:
            debug_log.debug("getting all model data".format())
            connection = get_db()
            cursor = connection.cursor(buffered=True)
            query = "SELECT model_id, model_content, description, solver_type  FROM optim_model_data"
    
            cursor.execute(query)
            if cursor is None:
                return 400, "FAILED"
            else:
                rows = cursor.fetchall()
                if rows is not None:
                    return 200, rows
                else:
                    close_db()
                    return 500, "NOT_FOUND"
        except Exception:
            error_log.error("error for request_id:  {}".format(traceback.format_exc()))
            close_db()
            return 500, "FAILED"


def is_db_enabled():
    return osdf_config['deployment'].get('isDatabaseEnabled', False)
