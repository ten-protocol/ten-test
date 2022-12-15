#!/bin/bash


help_and_exit() {
    echo ""
    echo "Usage: $(basename "${0}") ssh_key=<key> --resource_group=<group> --name=<name> --size=<size>"
    echo " "
    echo "where: "
    echo "  ssh_key             *Required* The name of the SSH public key to use"
    echo "  resource_group      *Optional* The name of the resource group to use (default SystemTestHostedRunner)"
    echo "  name                *Optional* The name of the VM instance (default LocalTestnetRunner) "
    echo "  size                *Optional* The instance type (default Standard_DC4s_v2)"
    echo ""
    exit 1
}

resource_group=SystemTestHostedRunner
name=LocalTestnetRunner
size=Standard_DC4s_v2

for argument in "$@"
do
    key=$(echo $argument | cut -f1 -d=)
    value=$(echo $argument | cut -f2 -d=)

    case "$key" in
            --ssh_key)                  ssh_key=${value} ;;
            --resource_group)           resource_group=${value} ;;
            --name)                     name=${value} ;;
            --size)                     size=${value} ;;
            --help)                     help_and_exit ;;
            *)
    esac
done

if [[ -z ${ssh_key:-} ]];
then
    help_and_exit
fi

# create the resource group
az group create --name ${resource_group} --location uksouth

# create the vm in the resources group
az vm create --resource-group ${resource_group} --name ${name} --image Canonical:0001-com-ubuntu-server-focal:20_04-lts-gen2:20.04.202206220  --size ${size} --admin-username azureuser --ssh-key-values ${ssh_key}

# run installation steps
az vm run-command invoke \
  --resource-group ${resource_group} \
  --name ${name} \
  --command-id RunShellScript \
  --scripts "apt update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata \
    && apt-get install -y software-properties-common \
    && add-apt-repository --yes ppa:ethereum/ethereum \
    && apt update \
    && apt install -y solc \
    && curl -sL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && npm install console-stamp --global \
    && npm install web3 --global \
    && npm install ethers --global \
    && npm install commander --global  \
    && npm install -g ganache  \
    && npm install -g ganache-cli \
    && apt install -y vim \
    && apt install -y python3-pip \
    && python3 -m pip install web3 \
    && python3 -m pip install pysys==1.6.1 \
    && python3 -m pip install py-solc-x \
    && snap install go --classic \
    && curl -fsSL https://get.docker.com -o get-docker.sh \
    && sh ./get-docker.sh"
