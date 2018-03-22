#!/bin/bash

# The script starts in the root folder of the repo, which has the following outline
# We fetch the version information from version.properties, build docker files and
# do a docker push. Since the job will be run under Jenkins, it will have the Nexus
# credentials
#
#  ├── docker
#  │   ├── Dockerfile
#  │   └── build_image.sh   <--- THIS SCRIPT is here
#  ├── docs
#  ├── osdf
#  ├── pom.xml
#  ├── test
#  └── version.properties   <--- Version information here

set -e

# Folder settings
DOCKER_REPOSITORY=nexus3.onap.org:10003
ORG=onap
PROJECT=optf-osdf
IMAGE_NAME=$DOCKER_REPOSITORY/$ORG/$PROJECT

# Version properties
source version.properties
VERSION=$release_version

function log_ts() {  # Log message with timestamp
    echo [DEBUG LOG at $(date +%Y%m%d:%H%M%S)] "$@"
}

function build_image() {
     log_ts Building Image in folder: $PWD
     docker build -t ${IMAGE_NAME}:${VERSION} -t ${IMAGE_NAME}:latest .
     log_ts ... Built
}

function push_image(){
     log_ts Pushing images: ${IMAGE_NAME}:\{$VERSION,latest\}
     docker push ${IMAGE_NAME}:${VERSION}
     docker push ${IMAGE_NAME}:latest
     log_ts ... Pushed images
}

set -e
(
  cd $(dirname $0)
  build_image
  push_image
)
