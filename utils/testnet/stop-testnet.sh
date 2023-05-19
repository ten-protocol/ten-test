#!/bin/bash

script_path="$(cd "$(dirname "${0}")" && pwd)"
root_path="${script_path}/../../../"

# remove existing containers (stops also)
for i in `docker ps -a | awk '{ print $1 } ' | grep -v CONTAINER`; do docker stop $i && docker rm $i; done
docker system prune -af --volumes
for i in `docker volume ls --filter dangling=true -q`; do docker volume rm $i; done
