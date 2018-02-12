import json
import unittest

from osdf.models.api.placementRequest import PlacementAPI
from osdf.models.api.placementResponse import PlacementResponse
from schematics.exceptions import ModelValidationError


class TestReqValidation(unittest.TestCase):

    def test_req_validation(self):
        req_file = "./test/placement-tests/request.json"
        req_json = json.loads(open(req_file).read())
        self.assertEqual(PlacementAPI(req_json).validate(), None)

    def test_req_failure(self):
        req_json = {}
        self.assertRaises(ModelValidationError, lambda: PlacementAPI(req_json).validate())


class TestResponseValidation(unittest.TestCase):

    def test_invalid_response(self):
        resp_json = {}
        self.assertRaises(ModelValidationError, lambda: PlacementResponse(resp_json).validate())


if __name__ == "__main__":
    unittest.main()
