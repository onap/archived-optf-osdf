# -------------------------------------------------------------------------
#   Copyright (c) 2018 AT&T Intellectual Property
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

from collections import defaultdict
from osdf.logging.osdf_logging import debug_log
from osdf.config.base import osdf_config


def retrieve_version_info(request, request_id):
    version_info_dict = defaultdict(dict)
    config = osdf_config.deployment 
    placement_ver_enabled = config.get('placementVersioningEnabled', False)

    if placement_ver_enabled: 
        placement_major_version = config.get('placementMajorVersion', None)
        placement_minor_version = config.get('placementMinorVersion', None)  
        placement_patch_version = config.get('placementPatchVersion', None)
        
        http_header = request.headers.environ
        http_x_minorversion = http_header.get("HTTP_X_MINORVERSION")
        http_x_patchversion = http_header.get("HTTP_X_PATCHVERSION")
        http_x_latestversion = http_header.get("HTTP_X_LATESTVERSION")
        
        debug_log.debug("Versions sent in HTTP header for request ID {} are: X-MinorVersion: {}  X-PatchVersion: {}  X-LatestVersion: {}"
                        .format(request_id, http_x_minorversion, http_x_patchversion, http_x_latestversion))
        debug_log.debug("latest versions specified in osdf config file are: placementMajorVersion: {}  placementMinorVersion: {}  placementPatchVersion: {}"
                        .format(placement_major_version, placement_minor_version, placement_patch_version))
    else:
        placement_major_version = config.get('placementDefaultMajorVersion', "1")
        placement_minor_version = config.get('placementDefaultMinorVersion', "0")
        placement_patch_version = config.get('placementDefaultPatchVersion', "0")
        
        debug_log.debug("Default versions specified in osdf config file are: placementDefaultMajorVersion: {}  placementDefaultMinorVersion: {}  placementDefaultPatchVersion: {}"
                        .format(placement_major_version, placement_minor_version, placement_patch_version))
        
    version_info_dict.update({
                               'placementVersioningEnabled': placement_ver_enabled,
                               'placementMajorVersion': str(placement_major_version),
                               'placementMinorVersion': str(placement_minor_version),
                               'placementPatchVersion': str( placement_patch_version)
                              })
    
    return version_info_dict  
    