# Setup and manage a remote Azure github runner

## Create and connect
Run the utility scripts to create the VM and connect;

```bash
# create the VM
 ./create-runner.sh --name=ten-test-gh-runner-01 
 
# connect to the VM
./connect-runner.sh --name=ten-test-gh-runner-01  
```

## Install dependencies
Once connected to the VM run `sudo ./install.sh` script to install all the required dependencies for running the tests. 
Once done ensure the correct version of solc is used, and set permissions for docker using the below;

```bash
# install and use 0.8.18
solc-select install 0.8.18
solc-select use 0.8.18

# put this in the .bashrc file to doubly ensure it is picked up by the runner
export SOLC_VERSION=0.8.18

# set permissions for docker
sudo groupadd docker
sudo usermod -aG docker tenadmin
newgrp docker
```

Note that we need to use go 1.21.13, and more recent VMs may come with a later version. To install 1.21.13 see the 
[go installation](https://go.dev/doc/install) guide, download `go1.21.13.linux-amd64.tar.gz` and install by unpacking 
and symbolically linking using;

```bash
sudo rm -rf /usr/local/go
sudo tar -C /usr/local -xzf go1.21.13.linux-amd64.tar.gz
sudo ln -s /usr/local/go/bin/go /usr/local/bin/go 
```

Note also you may want to resize the VM in the Azure portal for it's intended use, i.e. if running local testnet tests
on the runner use `Standard D8as v4 (8 vcpus, 32 GiB memory)`, and for running remote tests use
`Standard D4as v4 (4 vcpus, 16 GiB memory)`. The default is `Standard D4as v4`.

## Configure the runner
Go to the [runners](https://github.com/ten-protocol/ten-test/settings/actions/runners) section of the `ten-test`
repo and click on new runner. Follow the commands there to install and run the new runner. 

## Known issues
For an unknown reason on Azure Ubuntu VMs the `/var/lib/docker/overlay2` folder can grow even through all containers, 
images, volumes etc have been removed. Should the VM run out of diskspace, perform the following to manually delete;

```bash
sudo systemctl stop docker
sudo rm -rf /var/lib/docker/
sudo systemctl start docker
```
