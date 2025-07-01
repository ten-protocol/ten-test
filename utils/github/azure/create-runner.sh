#!/bin/bash

help_and_exit() {
    echo ""
    echo "Usage: $(basename "${0}") ssh_key=<key> --name=<name>"
    echo " "
    echo "where: "
    echo "  ssh_key             *Optional* The name of the SSH public key to use (default ~/.ssh/id_rsa.pub)"
    echo "  name                *Optional* The name of the VM instance (default ten-test-gh-runner) "
    echo ""
    exit 1
}

ssh_key=~/.ssh/id_rsa.pub
name=ten-test-gh-runner
group=ten-test-repo

for argument in "$@"
do
    key=$(echo $argument | cut -f1 -d=)
    value=$(echo $argument | cut -f2 -d=)

    case "$key" in
            --ssh_key)                  ssh_key=${value} ;;
            --name)                     name=${value} ;;
            --help)                     help_and_exit ;;
            *)
    esac
done

# create the resource group
echo "Creating resource group ..."
if [ $(az group exists --name ${group}) = false ]; then
  az group create --name ${group} --location uksouth
fi

# create the vm in the resources group
echo "Creating virtual machine ..."
az vm create --resource-group ${group} --name ${name} --image Canonical:0001-com-ubuntu-server-jammy:22_04-lts-gen2:latest --size Standard_D4as_v4 --admin-username tenadmin --ssh-key-values ${ssh_key} --nic-delete-option delete --os-disk-delete-option delete
sleep 30

# connect using given SSH key
echo "Transferring the install script ... "
ssh_private=`echo id_rsa.pub | sed 's/.pub//g'`
IP=`az vm show -d -g ${group} -n ${name} --query publicIps -o tsv`
scp -i ${ssh_private} -o StrictHostKeyChecking=no install.sh tenadmin@$IP:~

