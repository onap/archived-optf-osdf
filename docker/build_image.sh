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
SNAPSHOT=$snapshot_version
STAGING=${release_version}-STAGING
TIMESTAMP=$(date +"%Y%m%dT%H%M%S")Z
REPO=""

BUILD_ARGS="--no-cache"
if [ $HTTP_PROXY ]; then
    BUILD_ARGS+=" --build-arg HTTP_PROXY=${HTTP_PROXY}"
fi
if [ $HTTPS_PROXY ]; then
    BUILD_ARGS+=" --build-arg HTTPS_PROXY=${HTTPS_PROXY}"
fi

function log_ts() {  # Log message with timestamp
    echo [DEBUG LOG at $(date -u +%Y%m%d:%H%M%S)] "$@"
}

function get_artifact_version() {
    log_ts Get Maven Artifact version from pom.xml
    MVN_ARTIFACT_VERSION=`echo -e "setns x=http://maven.apache.org/POM/4.0.0 \n  xpath /x:project/x:version/text() "| xmllint --shell pom.xml | grep content | sed 's/.*content=//'`
    log_ts Maven artifact version for OSDF is $MVN_ARTIFACT_VERSION
    if [[ "$MVN_ARTIFACT_VERSION" =~ SNAPSHOT ]]; then
        log_ts "REPO is snapshots";
        REPO=snapshots
    else
        log_ts "REPO is releases";
        REPO=releases
    fi
    BUILD_ARGS+=" --build-arg REPO=${REPO}"
    BUILD_ARGS+=" --build-arg MVN_ARTIFACT_VERSION=${MVN_ARTIFACT_VERSION}"
}

function build_image() {
    log_ts Building Image in folder: $PWD with build arguments ${BUILD_ARGS}
    docker build ${BUILD_ARGS} -t ${IMAGE_NAME}:latest .
    log_ts ... Built
}

function push_image() {
    if [[ "$REPO" == snapshots ]]; then
        push_snapshot_image
    else
        push_staging_image
    fi
}


function push_snapshot_image(){
    log_ts Tagging images: ${IMAGE_NAME}:\{${SNAPSHOT}-${TIMESTAMP},${SNAPSHOT}-latest\}
    docker tag ${IMAGE_NAME}:latest ${IMAGE_NAME}:${SNAPSHOT}-${TIMESTAMP}
    docker tag ${IMAGE_NAME}:latest ${IMAGE_NAME}:${SNAPSHOT}-latest
    log_ts ... Tagged images

    log_ts Pushing images: ${IMAGE_NAME}:\{${SNAPSHOT}-${TIMESTAMP},${SNAPSHOT}-latest\}
    docker push ${IMAGE_NAME}:${SNAPSHOT}-${TIMESTAMP}
    docker push ${IMAGE_NAME}:${SNAPSHOT}-latest
    log_ts ... Pushed images
}

function push_staging_image(){
    log_ts Tagging images: ${IMAGE_NAME}:\{${STAGING}-${TIMESTAMP},${STAGING}-latest\}
    docker tag ${IMAGE_NAME}:latest ${IMAGE_NAME}:${STAGING}-${TIMESTAMP}
    docker tag ${IMAGE_NAME}:latest ${IMAGE_NAME}:${STAGING}-latest
    log_ts ... Tagged images

    log_ts Pushing images: ${IMAGE_NAME}:\{${STAGING}-${TIMESTAMP},${STAGING}-latest\}
    docker push ${IMAGE_NAME}:${STAGING}-${TIMESTAMP}
    docker push ${IMAGE_NAME}:${STAGING}-latest
    log_ts ... Pushed images
}

(
    get_artifact_version
    # Switch to docker build directory
    cd $(dirname $0)
    build_image
    push_image
)
