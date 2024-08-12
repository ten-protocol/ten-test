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

# run up the container
docker network inspect node_network > /dev/null 2>&1
if [ $? -eq 0 ]; then
    docker run -it -e DOCKER_TEST_ENV=true --network=node_network --name=e2e-tests testnetobscuronet.azurecr.io/obscuronet/obscuro_test:${version}
else
    docker run -it -e DOCKER_TEST_ENV=true --name=e2e-tests testnetobscuronet.azurecr.io/obscuronet/obscuro_test:${version}
fi

