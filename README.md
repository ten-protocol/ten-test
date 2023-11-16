<h1 align="center">
  <picture>
    <img alt="ten logo" src=".assets/ten_banner.png"/>
  </picture>
  Ten Protocol Test Framework 
</h1>

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
![Python](https://img.shields.io/badge/python-3.9-blue.svg)
[![Run local tests](https://github.com/ten-protocol/ten-test/actions/workflows/run_local_tests.yml/badge.svg)](https://github.com/ten-protocol/ten-test/actions/workflows/run_local_tests.yml)
[![Run merge tests](https://github.com/ten-protocol/ten-test/actions/workflows/run_merge_tests.yml/badge.svg)](https://github.com/ten-protocol/ten-test/actions/workflows/run_merge_tests.yml)

Project repo for running end to end system tests against a variety of networks, with [ten](https://obscu.ro/) being 
the primary network under test. Other networks supported include [ganache](https://trufflesuite.com/ganache/), 
[goerli via infura](https://infura.io/), [arbitrum](https://arbitrum.io/) and [sepolia](https://sepolia.dev/). The repo 
uses the [pysys](https://pysys-test.github.io/pysys-test/) test framework to manage all tests and their execution. All 
tests are fully system level using [web3.py](https://web3py.readthedocs.io/en/stable/) to interact with the networks 
which are managed outside the scope of the tests (with the exception of ganache which can be started locally). Note the 
project is currently under active development and further information on running the tests will be added to this readme
over time. 

Repository Structure
--------------------
The top level structure of the project is as below;

```
├── README.md            # Readme 
├── .github              # Github configuration including workflows
├── .default.properties  # Default properties file detailing connection and keys required for running 
├── pysysproject.xml     # The pysys project file detailing configuration options
├── get_artifacts.sh     # Build script to build artifacts from go-ten required for running Ten protocol tests
├── admin                # Used for administering the Ten testnet 
├── artifacts            # Directory to store artifacts for running Ten tests
├── src                  # The source root for all test code
│    ├── javascript      # A library of javascript client tooling
│    ├── python          # The python source root for pysys extensions
│    └── solidity        # A library of smart contracts 
├── tests                # The test root for all tests 
│    ├── generic         # Network agnostic tests 
│    └── ten             # Ten specific tests 
└── utils                # The project utils root for utilities used by the tests
     ├── docker          # Docker build and run files
     ├── github          # Azure VM github self hosted running build files
     ├── release         # Utilitiy scripts for making a new release of go-ten
     └── testnet         # Utilities for building and interacting with a local testnet
```

The [.default.properties](./.default.properties) file contains properties for running the tests that are common to any 
user. User specific properties should be added into a `~/.tentest/user.properties` file.  Properties will first be 
looked for in the `~/.tentest/user.properties` should it exist, and if not will fall back to the default properties. 


Setup and run locally using docker
----------------------------------
Should you wish to run the tests locally on your host machine against a local testnet, the easiest approach is to use
the docker image for the e2e tests. Prior to running, a local testnet should be built and run as described in the 
`go-ten/README.md` file (see the section "Building and running a local testnet"). Once the local testnet is running, 
the e2e docker image can be pulled down from the Azure container registry and run from the root of the `ten-test`
repository using the below; 

```bash
./utils/docker/run_image.sh --version=<version>
```

where version should be `latest` if the latest build from main is required, or otherwise the released version of 
`go-ten` and `ten-test` e.g. 0.19 , 0.18 etc. Note that this represents the head of the relevant releases 
branch and therefore will be the latest patch release of that major.minor version. 


Setup and run locally on host machine
-------------------------------------
As stated earlier, running the tests requires the `ten-test` repository to be cloned in the same parent directory 
as `go-ten`, and the dependent artifacts to be built (these are the wallet extension, and the ABIs for the bridge
contracts). To build the artifacts run `./get_artifacts.sh` in the root of the `ten-test` checkout. To install all 
dependencies for running the tests use the following on OSX or Linux accordingly;

### OSX (Monterey 12.4)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew update
brew upgrade
brew install node
brew tap ethereum/ethereum
brew install ethereum
brew install solidity
brew install python
brew install gnuplot

npm install solc@0.8.15 --global
npm install console-stamp --global
npm install ganache --global
npm install ganache-cli --global
npm install web3@1.9.0 --global
npm install ethers@5.7.2 --global
npm install commander --global

pip3 install web3==5.31.3
pip3 install pysys==1.6.1
pip3 install solc-select
pip3 install py-solc-x
```

### Linux (Ubuntu 20.04)
```bash
apt update
DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata
apt-get install -y software-properties-common
add-apt-repository ppa:ethereum/ethereum
apt update
apt install -y curl
apt install -y solc
apt install -y gnuplot
apt install -y ethereum

curl -sL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs
npm install console-stamp --global
npm install ganache --global
npm install ganache-cli --global
npm install web3@1.9.0 --global
npm install ethers@5.7.2 --global
npm install commander --global

apt install -y python3-pip
python3 -m pip install web3==5.31.3
python3 -m pip install pysys==1.6.1
python3 -m pip install solc-select
python3 -m pip install py-solc-x
```

Once installed it should be possible to run all tests from the pysys.py cli as described in the following sections. Note
that depending on differences in your installation, and should you want to add in your own accounts on Goerli or Arbitrum, 
you may need to override the `.default.properties` file by creating a user specific properties file in
`~/.tentest/user.properties`. Common overrides will include the path to various binaries used when running the tests, 
and account details. An example of an override properties file is as given below where binary locations and the project ID 
for Goerli and Arbitrum are set as overrides, along with real accounts as set up within metamask;

```
[binaries.darwin]
solc = /opt/homebrew/bin/solc 
ganache = /opt/homebrew/bin/ganache-cli
node = /opt/homebrew/bin/node
node_path = /opt/homebrew/lib/node_modules

[env.all]
Account1PK=<private key of account 1 available e.g. via metamask>
Account2PK=<private key of account 2>
Account3PK=<private key of account 3>
Account4PK=<private key of account 4>

[env.goerli]
ProjectID = <id>

[env.arbitrum]
APIKey = <api key>
```

Print and run tests
--------------------
Each test is a separate directory within `ten-test/tests` where the directory name denotes the testcase id. Each 
test will contain a `run.py` file (the execution and validation steps) and a `pysystest.xml` file (metadata about the 
test such as its title, purpose, supported modes it can be run in). Note that the tests can be run against a variety 
of networks using the `-m mode` option. The E2E tests have specifically been designed such that any generic tests 
can be run against Ten, Ganache, Arbitrum or Goerli. To print out information on the tests, or to run them 
against a particular network, change directory to `ten-test/tests` and run as below;

```bash
# print out test titles
pysys.py print 

# print out full test details
pysys.py print -f

# run the tests against Ten sepolia-testnet
pysys.py run -m ten.sepolia

# run the tests against Ten uat-testnet
pysys.py run  -m ten.uat

# run the tests against Ten dev-testnet
pysys.py run -m ten.dev 

# run the tests against Ten local testnet
pysys.py run -m ten.local

# run the tests against a local ganache network 
pysys.py run -m ganache

# run the tests against the Arbitrum network 
pysys.py run -m arbitrum

# run the tests against the Goerli network 
pysys.py run -m goerli

# run the tests against the Sepolia network 
pysys.py run -m sepolia
```

Note that should you wish to run against a Ten local testnet, you will need to build and run the local testnet 
yourself using the approach as described in the [go-ten readme](https://github.com/ten-protocol/go-ten#building-and-running-a-local-testnet). 
Both the local testnet and the faucet will need to be started. To run against ganache the test framework will start the 
local ganache network on your behalf, and tear it down when test execution is complete. To run the same tests against 
Goerli or Arbitrum, the `~/.tentest/user.properties` should be created as described earlier. 


Running a specific test or range of tests
-----------------------------------------
The [pysys](https://pysys-test.github.io/pysys-test/) launch cli provides a rich interface to allow you to run a 
specific test, ranges of tests, or groups of tests, as well as running them in different modes, with different 
verbosity logging, and in cycles. See the cli documentation for more detail using `pysys.py run -h`. When running tests 
pysys will search the directory tree for all tests available from the current working directory downwards, and then 
filter based on the user request e.g. 


```bash
# run a specific test
pysys.py run -m ten.sepolia gen_cor_001

# run a range of tests (using python list slicing syntax)
pysys.py run -m ten.sepolia gen_cor_001:gen_cor_004
pysys.py run -m ten.sepolia gen_cor_003:

# run a test multiple times
pysys.py run -m ten.sepolia -c 5 gen_cor_003

# run a test with full verbosity logging
pysys.py run -m ten.sepolia -v DEBUG gen_cor_003
```






