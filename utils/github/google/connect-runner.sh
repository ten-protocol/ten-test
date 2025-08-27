#!/bin/bash

help_and_exit() {
    echo ""
    echo "Usage: $(basename "${0}") --ssh_key=<key> --name=<name> --zone=<zone>"
    echo " "
    echo "where: "
    echo "  ssh_key   *Optional* Path to the SSH private key (default: ~/.ssh/id_rsa)"
    echo "  name      *Optional* Name of the VM instance (default: ten-test-google-runner-01)"
    echo "  zone      *Optional* GCP zone where the VM resides (default: europe-west1-b)"
    echo ""
    exit 1
}

ssh_key=~/.ssh/id_rsa
name=ten-test-google-runner-01
zone=europe-west2-a

for argument in "$@"
do
    key=$(echo $argument | cut -f1 -d=)
    value=$(echo $argument | cut -f2 -d=)

    case "$key" in
            --ssh_key) ssh_key=${value} ;;
            --name)    name=${value} ;;
            --zone)    zone=${value} ;;
            --help)    help_and_exit ;;
            *)
    esac
done

# get the IP
echo "Instance in zone $zone"
gcloud compute instances list --filter="name=(${name})" --zones "${zone}" --format="table(name, networkInterfaces.accessConfigs.natIP)"

IP=$(gcloud compute instances list --filter="name=(${name})" --zones "${zone}" --format="get(networkInterfaces[0].accessConfigs[0].natIP)")

if [[ -z "$IP" ]]; then
  echo "Could not find instance $name in zone $zone"
  exit 1
fi

# connect using given SSH key
echo "Connecting to ${name} ..."
gcloud compute ssh ${name} --zone ${zone}

