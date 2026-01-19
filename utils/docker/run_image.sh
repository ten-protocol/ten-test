#!/usr/bin/env bash
# Script to run the latest image of the VM for running ten test
#
help_and_exit() {
    echo ""
    echo "Usage: $(basename "${0}") --version=<version>"
    echo " "
    echo "where: "
    echo "  version             *Optional* The name of the version to use (default latest)"
    echo ""
    exit 1
}

version=latest

for argument in "$@"
do
    key=$(echo $argument | cut -f1 -d=)
    value=$(echo $argument | cut -f2 -d=)

    case "$key" in
            --version)                  version=${value} ;;
            --help)                     help_and_exit ;;
            *)
    esac
done

# remove a previously running container if it exists
docker rm --volumes e2e-tests

# detect architecture of running host
ARCH=$(uname -m)
PLATFORM_ARG=""

if [[ "$ARCH" == "arm64" || "$ARCH" == "aarch64" ]]; then
    PLATFORM_ARG="--platform=linux/amd64"
fi

echo "Detected architecture: $ARCH"
echo "Using Docker platform args: ${PLATFORM_ARG:-default}"

# run up the container
docker network inspect node_network > /dev/null 2>&1
if [ $? -eq 0 ]; then
    docker run ${PLATFORM_ARG} -it -e DOCKER_TEST_ENV=true --network=node_network --name=e2e-tests testnetobscuronet.azurecr.io/obscuronet/obscuro_test:${version}
else
    docker run ${PLATFORM_ARG} -it -e DOCKER_TEST_ENV=true --name=e2e-tests testnetobscuronet.azurecr.io/obscuronet/obscuro_test:${version}
fi

