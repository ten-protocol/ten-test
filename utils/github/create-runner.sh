#!/bin/bash

help_and_exit() {
    echo ""
    echo "Usage: $(basename "${0}") ssh_key=<key> --name=<name>"
    echo " "
    echo "where: "
    echo "  ssh_key             *Optional* The name of the SSH public key to use (default ~/.ssh/id_rsa.pub)"
    echo "  name                *Optional* The name of the VM instance (default obscuro-test-gh-runner) "
    echo ""
    exit 1
}

ssh_key=~/.ssh/id_rsa.pub
name=obscuro-test-gh-runner
group=obscuro-test-repo

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
az vm create --resource-group ${group} --name ${name} --image Canonical:0001-com-ubuntu-server-focal:20_04-lts-gen2:20.04.202206220  --size Standard_DC4s_v2 --admin-username obscuro --ssh-key-values ${ssh_key} --nic-delete-option delete --os-disk-delete-option delete
sleep 30

# connect using given SSH key
echo "Transferring the install script ... "
IP=`az vm show -d -g ${group}  -n ${name} --query publicIps -o tsv`
scp -i ${ssh_key} install.sh obscuro@$IP:~

