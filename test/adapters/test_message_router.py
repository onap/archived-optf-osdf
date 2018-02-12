import osdf.adapters.dcae.message_router as MR
import unittest

from osdf.operation.exceptions import MessageBusConfigurationException
from unittest.mock import patch


class TestMessageRouter(unittest.TestCase):

    def test_valid_MR(self):
        mr = MR.MessageRouterClient(dmaap_url="https://MYHOST:3905")

    def test_valid_MR_with_base_urls(self):
        base_urls = ["https://MYHOST1:3905/","https://MYHOST2:3905/"]
        mr = MR.MessageRouterClient(mr_host_base_urls=base_urls, topic="MY-TOPIC")

    def test_invalid_valid_MR_with_base_urls(self):
        """Topic missing"""
        base_urls = ["https://MYHOST1:3905/","https://MYHOST2:3905/"]
        try:
            mr = MR.MessageRouterClient(mr_host_base_urls=base_urls)
        except MessageBusConfigurationException:
            return

        raise Exception("Allows invalid MR configuration") # if it failed to error out

    @patch('osdf.adapters.dcae.message_router.MessageRouterClient.http_request', return_value={})
    def test_mr_http_request_mocked(self, http_request):
        mr = MR.MessageRouterClient(dmaap_url="https://MYHOST:3905")
        mr.http_request = http_request
        assert mr.get() == {} 
        assert mr.post("Hello") == {} 

    def test_mr_http_request_non_existent_host(self):
        mr = MR.MessageRouterClient(dmaap_url="https://MYHOST:3905")
        try:
            mr.get()
        except:
            return

        raise Exception("Allows invalid host") # if it failed to error out
if __name__ == "__main__":
    unittest.main()

