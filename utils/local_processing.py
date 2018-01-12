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

import os

from osdf.logging.osdf_logging import metrics_log, MH, warn_audit_error


def local_create_job_file(req_id, json_req, fname='osdf-req-data.json'):
    """Creates a "work" folder for local processing and place relevant
    job task file in there"""

    work_dir = 'osdf-optim/work/' + req_id
    work_file = '{}/{}'.format(work_dir, fname)
    try:
        cur_task = "Making a local directory in the OSDF manager for req-id: {}".format(req_id)
        metrics_log.info(MH.creating_local_env(cur_task))
        os.makedirs(work_dir, exist_ok=True)
    except Exception as err:
        warn_audit_error(MH.error_local_env(req_id, "Can't create directory {}".format(work_dir), err))
        return None
    try:
        with open(work_file, 'w') as fid:
            fid.write(json_req['payload'])
        return work_dir
    except Exception as err:
        warn_audit_error(MH.error_local_env(req_id, "can't create file {}".format(work_file), err))
        return None
