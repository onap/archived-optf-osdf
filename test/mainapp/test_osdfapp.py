import osdfapp
import unittest

from osdf.operation.exceptions import BusinessException
from requests import Request, RequestException
from schematics.exceptions import DataError
from unittest import mock, TestCase
from unittest.mock import patch


class TestOSDFApp(TestCase):

    def setUp(self):
        self.patcher_g = patch('osdfapp.g', return_value={'request_id':'DUMMY-REQ'})
        self.Mock_g = self.patcher_g.start()
        # self.patcher2 = patch('package.module.Class2')
        # self.MockClass2 = self.patcher2.start()

    def tearDown(self):
        patch.stopall()

    def dummy_request_exception(self):
        e = RequestException("Web Request Exception Description")
        e.response = mock.MagicMock()
        e.request = Request(method="GET", url="SOME-URL")
        e.response.status_code = 400
        e.response.content = "Some request exception occurred"
        # request().raise_for_status.side_effect = e
        return e
 
    def test_handle_business_exception(self):
        e = BusinessException("Business Exception Description")
        resp = osdfapp.handle_business_exception(e)
        assert resp.status_code == 400

    def test_handle_request_exception(self):
        e = self.dummy_request_exception()
        resp = osdfapp.handle_request_exception(e)
        assert resp.status_code == 400

    def test_handle_data_error(self):
        e = DataError({"A1": "A1 Data Error"})
        resp = osdfapp.handle_data_error(e)
        assert resp.status_code == 400

    def test_internal_failure(self):
        e = Exception("An Internal Error")
        resp = osdfapp.internal_failure(e)
        assert resp.status_code == 500

    def test_getOptions_default(self):
        opts = osdfapp.getOptions(["PROG"])  # ensure nothing breaks


if __name__ == "__main__":
    unittest.main()

