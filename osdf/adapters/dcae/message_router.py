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


class MessageRouterClient(object):
    def __init__(self,
                 dmaap_url=None,
                 mr_host_base_urls=None,
                 topic=None,
                 consumer_group=None, consumer_id=None,
                 timeout_ms=15000, fetch_limit=1000,
                 userid=None, passwd=None):
        """
        :param dmaap_url: protocol, host and port; mostly for UEB
               (e.g. https://dcae-msrt-ftl.homer.att.com:3905/)
        :param mr_host_base_urls: for DMaaP, we get a topic URL (base_url + events/topic_name)
               (e.g. https://dcae-msrt-ftl.homer.att.com:3905/events/com.att.dcae.dmaap.FTL.SNIRO-CM-SCHEDULER-RESPONSE)
        :param consumer_group: DMaaP/UEB consumer group (unique for each subscriber; required for GET)
        :param consumer_id: DMaaP/UEB consumer ID (unique for each thread/process for a subscriber; required for GET)
        :param timeout_ms: (optional, default 15 seconds or 15,000 ms) server-side timeout for GET request
        :param fetch_limit: (optional, default 1000 messages per request for GET), ignored for "POST"
        :param userid: (optional, userid for HTTP basic authentication)
        :param passwd: (optional, password for HTTP basic authentication)
        """
        mr_error = MessageBusConfigurationException
        if dmaap_url is None:  # definitely not DMaaP, so use UEB mode
            self.is_dmaap = False
            if not (mr_host_base_urls and list_like(mr_host_base_urls)):
                raise mr_error("Not a DMaaP or UEB configuration")
            if not topic:
                raise mr_error("Invalid topic: '{}'",format(topic))
            self.topic_urls = ["{}/events/{}".format(base_url, topic) for base_url in mr_host_base_urls]
        else:
            self.is_dmaap = True
            self.topic_urls = [dmaap_url]

        self.timeout_ms = timeout_ms
        self.fetch_limit = fetch_limit
        self.auth = (userid, passwd) if userid and passwd else None
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
        res = requests.request(url=url, method=method, auth=self.auth, **kwargs)
        if res.status_code == requests.codes.ok:
            return res.json() if outputjson or method == "POST" else res.content
        else:
            raise Exception("HTTP Response Error: code {}; headers:{}, content: {}".format(
                res.status_code, res.headers, res.content))
