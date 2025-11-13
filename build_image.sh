#!/bin/bash

version="$1"
[[ -z $version ]] && {
    echo "No version given"
    exit 1
}

[[ -z $CASUAL_PERFORMANCE_IMAGE_REPO ]] && {
    echo "'CASUAL_PERFORMANCE_IMAGE_REPO' is not set"
    exit 1
}

echo "Building casual-performance:$version"
docker build -t casual-performance:${version} --build-arg CASUAL_VERSION=${version} -f docker/casual-performance/Dockerfile .

echo "Pushing ${CASUAL_PERFORMANCE_IMAGE_REPO}/casual-performance:${version}"
docker tag casual-performance:${version} ${CASUAL_PERFORMANCE_IMAGE_REPO}/casual-performance:${version}
docker image push ${CASUAL_PERFORMANCE_IMAGE_REPO}/casual-performance:${version}