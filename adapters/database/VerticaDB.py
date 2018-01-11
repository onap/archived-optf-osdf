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

import jaydebeapi
import sqlalchemy.pool as pool

from jaydebeapi import _DEFAULT_CONVERTERS, _java_to_py
from osdf.utils.programming_utils import MetaSingleton
from osdf.config.base import osdf_config

_DEFAULT_CONVERTERS.update({'BIGINT': _java_to_py('longValue')})


class VerticaDB(metaclass=MetaSingleton):
    connection_pool = None

    def get_connection(self):
        p = self.get_config_params()
        c = jaydebeapi.connect(
            'com.vertica.jdbc.Driver',
            'jdbc:vertica://{}:{}/{}'.format(p['host'], p['port'], p['db']),
            {'user': p['user'], 'password': p['passwd'], 'CHARSET': 'UTF8'},
            jars=[p['db_driver']]
        )
        return c

    def get_config_params(self):
        config = osdf_config["deployment"]
        host, port, db = config["verticaHost"], config["verticaPort"], config.get("verticaDB")
        user, passwd = config["verticaUsername"], config["verticaPassword"]
        jar_path = osdf_config['core']['osdf_system']['vertica_jar']
        params = dict(host=host, db=db, user=user, passwd=passwd, port=port, db_driver=jar_path)
        return params

    def connect(self):
        if self.connection_pool is None:
            self.connection_pool = pool.QueuePool(self.get_connection, max_overflow=10, pool_size=5, recycle=600)
        conn = self.connection_pool.connect()
        cursor = conn.cursor()
        return conn, cursor
