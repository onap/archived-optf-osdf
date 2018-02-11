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

"""Core functions for OSDF Application, including flask app"""

from jinja2 import Template


end_point_auth_mapping = {  # map a URL endpoint to auth group
    "cmscheduler": "CMScheduler",
    "placement": "Placement",
}

userid_suffix, passwd_suffix = "Username", "Password"
auth_groups = set(end_point_auth_mapping.values())

ERROR_TEMPLATE = Template("""
{
     "serviceException": {
        "text": "{{ description }}"
     }
}
""")

ACCEPTED_MESSAGE_TEMPLATE = Template("""
{
   "requestId": "{{ request_id }}",
   "text": "{{ description }}"
}
""")
