
import unittest
from unittest.mock import patch
import osdf.config.loader as config_loader
import pytest
from apps.nxi_termination.optimizers.remote_opt_processor import process_nxi_termination_opt


from osdf.config.base import osdf_config
from osdf.utils.programming_utils import DotDict
from osdf.utils.interfaces import json_from_file

class TestRemoteOptProcessor(unittest.TestCase):
    def setUp(self):
        self.config_spec = {
            "deployment": "config/osdf_config.yaml",
            "core": "config/common_config.yaml"
        }
        self.osdf_config = DotDict(config_loader.all_configs(**self.config_spec))

    def tearDown(self):

        patch.stopall()

    def test_process_nxi_termination_opt(self):
        main_dir = ""
        request_file = main_dir + 'test/apps/nxi_termination/nxi_termination.json'
        nssi_request_file=main_dir + 'test/apps/nxi_termination/nssi_termination.json'
        service_file = main_dir + 'test/apps/nxi_termination/service_profiles.json'
        failure_service_file = main_dir + 'test/apps/nxi_termination/failure_service_profiles.json'
        failure_service_file2 = main_dir + 'test/apps/nxi_termination/failure_service_profiles2.json'
        nsi_success=main_dir + 'test/apps/nxi_termination/nsi_success_output.json'
        nxi_failure1 = main_dir + 'test/apps/nxi_termination/nxi_failure_output1.json'
        nxi_failure2 = main_dir + 'test/apps/nxi_termination/nxi_failure_output2.json'
        nssi_failure = main_dir + 'test/apps/nxi_termination/nssi_failure_output.json'
        success_rel_file = main_dir + 'test/apps/nxi_termination/success_relationship_list.json'
        failure_rel_file1 = main_dir + 'test/apps/nxi_termination/failure_relationship_list.json'
        failure_rel_file2 = main_dir + 'test/apps/nxi_termination/failure_relationship_list2.json'
        request_json=json_from_file(request_file)
        nssi_request_json = json_from_file(nssi_request_file)
        service_profile_json = json_from_file(service_file)
        failure_service_profile_json = json_from_file(failure_service_file)
        failure_service_profile_json2 = json_from_file(failure_service_file2)
        success_rel_json=json_from_file(success_rel_file)
        failure_rel_json = json_from_file(failure_rel_file1)
        failure_rel_json2 = json_from_file(failure_rel_file2)
        success_output_json=json_from_file(nsi_success)
        nxi_failure_output_json1 = json_from_file(nxi_failure1)
        nxi_failure_output_json2 = json_from_file(nxi_failure2)
        nssi_failure_output_json = json_from_file(nssi_failure)

        #nsi success scenario
        self.patcher_req=patch('apps.nxi_termination.optimizers.remote_opt_processor.get_service_profiles',return_value=service_profile_json)
        self.Mock_req = self.patcher_req.start()
        self.assertEquals(success_output_json, process_nxi_termination_opt(request_json,osdf_config))
        self.patcher_req.stop()

        #nsi failure scenario
        self.patcher_req = patch('apps.nxi_termination.optimizers.remote_opt_processor.get_service_profiles', return_value=failure_service_profile_json)
        self.Mock_req = self.patcher_req.start()
        self.assertEquals(nxi_failure_output_json1, process_nxi_termination_opt(request_json, osdf_config))
        self.patcher_req.stop()

        #nsi success scenario
        self.patcher_req = patch('apps.nxi_termination.optimizers.remote_opt_processor.get_service_profiles',
                                 return_value=[])
        self.Mock_req = self.patcher_req.start()
        self.assertEquals(success_output_json, process_nxi_termination_opt(request_json, osdf_config))
        self.patcher_req.stop()

        # nsi failure scenario
        self.patcher_req = patch('apps.nxi_termination.optimizers.remote_opt_processor.get_service_profiles',
                                 return_value=failure_service_profile_json2)
        self.Mock_req = self.patcher_req.start()
        self.assertEquals(nxi_failure_output_json2, process_nxi_termination_opt(request_json, osdf_config))
        self.patcher_req.stop()
        # #
        # nssi success scenario
        self.patcher_req = patch('apps.nxi_termination.optimizers.remote_opt_processor.get_relationshiplist', return_value=success_rel_json)
        self.Mock_req = self.patcher_req.start()
        self.assertEquals(success_output_json, process_nxi_termination_opt(nssi_request_json, osdf_config))
        self.patcher_req.stop()

        # nssi success scenario
        self.patcher_req = patch('apps.nxi_termination.optimizers.remote_opt_processor.get_relationshiplist',
                                 return_value=[])
        self.Mock_req = self.patcher_req.start()
        self.assertEquals(success_output_json, process_nxi_termination_opt(nssi_request_json, osdf_config))
        self.patcher_req.stop()

        # nssi failure scenario
        self.patcher_req = patch('apps.nxi_termination.optimizers.remote_opt_processor.get_relationshiplist',
                                 return_value=failure_rel_json)
        self.Mock_req = self.patcher_req.start()
        self.assertEquals(nssi_failure_output_json, process_nxi_termination_opt(nssi_request_json, osdf_config))
        self.patcher_req.stop()

        # nssi failure scenario
        self.patcher_req = patch('apps.nxi_termination.optimizers.remote_opt_processor.get_relationshiplist',
                                 return_value=failure_rel_json2)
        self.Mock_req = self.patcher_req.start()
        self.assertEquals(nxi_failure_output_json2, process_nxi_termination_opt(nssi_request_json, osdf_config))
        self.patcher_req.stop()

        # #
        # # # nssi failure scenario
        # self.patcher_req = patch('osdf.adapters.aai.fetch_aai_data.get_aai_data', return_value=nssi_failure_json)
        # self.Mock_req = self.patcher_req.start()
        # self.assertEquals(nssi_failure_output_json, check_nssi_termination(request_json, osdf_config))
        # self.patcher_req.stop()

if __name__ == "__main__":
    unittest.main()