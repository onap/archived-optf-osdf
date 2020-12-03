# -------------------------------------------------------------------------
#   Copyright (c) 2015-2017 AT&T Intellectual Property
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

import os
from osdf.config.consulconfig import call_consul_kv
import osdf.config.credentials as creds
import osdf.config.loader as config_loader
from osdf.utils.programming_utils import DotDict
from threading import Thread

config_spec = {
    "deployment": os.environ.get("OSDF_CONFIG_FILE", "config/osdf_config.yaml"),
    "core": "config/common_config.yaml"
}

slicing_spec = "config/slicing_config.yaml"

slice_config = config_loader.load_config_file(slicing_spec)

osdf_config = DotDict(config_loader.all_configs(**config_spec))

http_basic_auth_credentials = creds.load_credentials(osdf_config)

dmaap_creds = creds.dmaap_creds()

creds_prefixes = {"so": "so", "cm": "cmPortal", "pcih": "pciHMS"}

osdf_config_deployment = osdf_config.deployment


if osdf_config.deployment.get('activateConsulConfig'):
    consulthread = Thread(target=call_consul_kv, args=(osdf_config,))
    consulthread.start()
