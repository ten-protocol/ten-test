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
echo "Creating resource group ..."
az group create --name ${resource_group} --location uksouth

# create the vm in the resources group
echo "Creating virtual machine ..."
az vm create --resource-group ${resource_group} --name ${name} --image Canonical:0001-com-ubuntu-server-focal:20_04-lts-gen2:20.04.202206220  --size ${size} --admin-username azureuser --ssh-key-values ${ssh_key}
sleep 10

# connect using given SSH key
echo "Transferring the install script ... "
IP=`az vm show -d -g ${resource_group}  -n ${name} --query publicIps -o tsv`
scp -i ${ssh_key} install.sh azureuser@$IP:~

