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

import requests
from osdf.utils.data_types import list_like
from osdf.operation.exceptions import MessageBusConfigurationException
from osdf.utils.interfaces import RestClient


class MessageRouterClient(object):
    def __init__(self,
                 dmaap_url='',
                 consumer_group_id=':',
                 timeout_ms=15000, fetch_limit=1000,
                 userid_passwd=':'):
        """
        :param dmaap_url: protocol, host and port; can also be a list of URLs
               (e.g. https://dmaap-host.onapdemo.onap.org:3905/events/org.onap.dmaap.MULTICLOUD.URGENT),
               can also be a list of such URLs
        :param consumer_group_id: DMaaP consumer group and consumer id (':' separated)
               consumer_group is unique for each subscriber; required for GET
               consumer_id: DMaaP consumer ID (unique for each thread/process for a subscriber; required for GET)
        :param timeout_ms: (optional, default 15 seconds or 15,000 ms) server-side timeout for GET request
        :param fetch_limit: (optional, default 1000 messages per request for GET), ignored for "POST"
        :param userid_passwd: (optional, userid:password for HTTP basic authentication)
        """
        mr_error = MessageBusConfigurationException
        if not dmaap_url:  # definitely not DMaaP, so use UEB mode
            raise mr_error("Not a valid DMaaP configuration")
        self.topic_urls = [dmaap_url] if not list_like(dmaap_url) else dmaap_url
        self.timeout_ms = timeout_ms
        self.fetch_limit = fetch_limit
        self.userid, self.passwd = userid_passwd.split(':')
        consumer_group, consumer_id = consumer_group_id.split(':')
        self.consumer_group = consumer_group
        self.consumer_id = consumer_id

    def get(self, outputjson=True):
        """Fetch messages from message router (DMaaP or UEB)
        :param outputjson: (optional, specifies if response is expected to be in json format), ignored for "POST"
        :return: response as a json object (if outputjson is True) or as a string
        """
        url_fmt = "{topic_url}/{cgroup}/{cid}?timeout={timeout_ms}&limit={limit}"
        urls = [url_fmt.format(topic_url=x, timeout_ms=self.timeout_ms, limit=self.fetch_limit,
                               cgroup=self.consumer_group, cid=self.consumer_id) for x in self.topic_urls]
        for url in urls[:-1]:
            try:
                return self.http_request(method='GET', url=url, outputjson=outputjson)
            except:
                pass
        return self.http_request(method='GET', url=urls[-1], outputjson=outputjson)

    def post(self, msg, inputjson=True):
        for url in self.topic_urls[:-1]:
            try:
                return self.http_request(method='POST', url=url, inputjson=inputjson, msg=msg)
            except:
                pass
        return self.http_request(method='POST', url=self.topic_urls[-1], inputjson=inputjson, msg=msg)

    def http_request(self, url, method, inputjson=True, outputjson=True, msg=None, **kwargs):
        """
        Perform the actual URL request (GET or POST), and do error handling
        :param url: full URL (including topic, limit, timeout, etc.)
        :param method: GET or POST
        :param inputjson: Specify whether input is in json format (valid only for POST)
        :param outputjson: Is response expected in a json format
        :param msg: content to be posted (valid only for POST)
        :return: response as a json object (if outputjson or POST) or as a string; None if error
        """

        rc = RestClient(userid=self.userid, passwd=self.passwd, url=url, method=method)
        try:
            res = rc.request(raw_response=True, data=msg, **kwargs)
            if res.status_code == requests.codes.ok:
                return res.json() if outputjson or method == "POST" else res.content
            else:
                raise Exception("HTTP Response Error: code {}; headers:{}, content: {}".format(
                    res.status_code, res.headers, res.content))

        except requests.RequestException as ex:
            raise Exception("Request Exception occurred {}".format(str(ex)))
