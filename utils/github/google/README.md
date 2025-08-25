# Setup and manage a remote Google github runner

## Create and connect
The VMs should be created manually from the Google console, into the europe-west2 region, with the instance type 
as `e2.standard-8` (8CPUs, 32GBs) or `e2.standard-4` (4CPUs, 16GBs), where the former is required for running 
local testnets. The `tenadmin` user should be created using the below;

```bash
# create the tenadmin user
sudo adduser tenadmin
sudo usermod -aG sudo tenadmin
```

Once done connection can be performed using the below where the name of the VM is supplied to the connection script. 
Setup of the VM is performed as for the azure instances, though the install.sh script needs to be scp'd to the box 
manually. 

```bash
# connect to the VM
./connect-runner.sh --name=ten-test-google-runner-01  
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

## Configure the runner
Go to the [runners](https://github.com/ten-protocol/ten-test/settings/actions/runners) section of the `ten-test`
repo and click on new runner. Follow the commands there to install and run the new runner. 

## Known issues
For an unknown reason on Ubuntu VMs the `/var/lib/docker/overlay2` folder can grow even though all containers, 
images, volumes etc have been removed. Should the VM run out of diskspace, perform the following to manually delete;

```bash
sudo systemctl stop docker
sudo rm -rf /var/lib/docker/
sudo systemctl start docker
```
