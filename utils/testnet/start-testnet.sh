#!/bin/bash

script_path="$(cd "$(dirname "${0}")" && pwd)"
root_path="${script_path}/../../../"

# build the containers
cd ${root_path}/obscuro-test/utils/testnet
docker compose -f docker-compose.local.yml build --parallel

# start up testnet and the faucet
cd ${root_path}/go-ten/
go run ./testnet/launcher/cmd

cd ${root_path}/go-ten/tools/faucet
./container_run.sh --image=testnetobscuronet.azurecr.io/obscuronet/faucet:latest