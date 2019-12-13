/*-
 * ============LICENSE_START=======================================================
 * ONAP OSDF
 * ================================================================================
 * Copyright (C) 2018 AT&T Intellectual Property. All rights
 *                             reserved.
 * ================================================================================
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * ============LICENSE_END============================================
 * ===================================================================
 * 
 */

package org.onap.osdf.maven.scripts

println project.properties['osdf.project.version']

def versionTag
if ( project.properties['osdf.project.version'] != null ) {
    versionArray = project.properties['osdf.project.version'].split('\\.|-');
    versionTag = versionArray[0] + '.' + versionArray[1] + '.' + versionArray[2]
    timestamp = project.properties['osdf.build.timestamp']
}

if ( project.properties['osdf.project.version'].endsWith("-SNAPSHOT") ) {
    project.properties['project.docker.latesttag.version']=versionTag + "-SNAPSHOT-latest";
    project.properties['project.docker.latesttagtimestamp.version']=versionTag + "-SNAPSHOT-"+timestamp;
    project.properties['project.repo'] = 'snapshots'
} else { 
    project.properties['project.docker.latesttag.version']=baseTag + "-STAGING-latest";
    project.properties['project.docker.latesttagtimestamp.version']=versionTag + "-STAGING-"+timestamp;
    project.properties['project.repo'] = 'releases'
} 

println 'New Tag for docker: ' + project.properties['project.docker.latesttag.version'];