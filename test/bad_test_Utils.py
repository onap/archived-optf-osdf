import unittest
import json

from osdf.config.base import osdf_config
from osdf.utils.programming_utils import dot_notation


class TestUtils(unittest.TestCase):

    def test_metrics(self):
        with open('test/placement-tests/request.json', 'r') as f:
            data = json.load(f)
            placementInfo = data["placementInfo"]
            config_local = osdf_config.core
            self.assertEqual("USOSTCDALTX0101UJZZ11", dot_notation(placementInfo, config_local['service_info']['vCPE']['vcpeHostName']))
            self.assertEqual("200", dot_notation(placementInfo, config_local['service_info']['vCPE']['e2eVpnKey']))
            self.assertEqual(['vGMuxInfra', 'vG'], dot_notation(placementInfo, 'demandInfo.placementDemand.resourceModuleName'))


if __name__ == '__main__':
    unittest.main()
