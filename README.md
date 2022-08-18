Obscuro Test Framework (multiple networks)
------------------------------------------
Project repo for running end to end system tests against a variety of networks, with [obscuro](https://obscu.ro/) being 
the primary network under test. Other networks supported include [ganache](https://trufflesuite.com/ganache/), 
[ropsten via infura](https://infura.io/), and [geth](https://geth.ethereum.org/docs/getting-started). The repo uses the 
[pysys](https://pysys-test.github.io/pysys-test/) test framework to manage all tests and their execution. All tests are 
fully system level using [web3.py](https://web3py.readthedocs.io/en/stable/) to interact with the networks which are 
managed outside the scope of the tests (with the exception of ganache which can be started locally). Note the project is 
currently under active development and further information on running the tests will be added to this readme over time. 


Repository Structure
--------------------
The top level structure of the project is as below;

```
├── README.md            # Readme 
├── .default.properties  # Default properties file detailing connection and keys required for running 
├── pysysproject.xml     # The pysys project file
├── admin                # Used for administering Obscuro testnet 
├── artifacts            # Artifacts used during test execution (e.g. Obscuro wallet extension)
├── src                  # The project source root for test execution 
│    └── python          # Python source code as extension to pysys for ethereum interaction
├── tests                # The project test root for all tests 
│    ├── generic         # Network agnostic tests 
│    └── obscuro         # Obscuro specific tests 
└── utils                # The project utils root for utilities used by the tests
     ├── contracts       # A library of smart contracts 
     └── docker          # Used to build and run a linux docker container to run the tests 
```

The [.default.properties](./.default.properties) file contains properties for running the tests that are common to any 
user. User specific properties should be added into a `.username.properties` file at the root of the project. As this 
file could contain sensitive data it should never be committed back into the main repo (the [.gitignore](./.gitignore) 
should prevent this). Properties will first be looked for in a `.username.properties` should it exist, and if not will 
fall back to the default properties. 


Quickstart Setup and Run
------------------------
The easiest way to set up a host to run the tests is to create a docker container with all dependencies pre-installed. 
The `obscuro-test` repository should be cloned into the same parent directory as 
[go-obscuro](https://github.com/obscuronet/go-obscuro) as running the tests will use the wallet_extension built from the 
working copy of the go-obscuro repository. To build the wallet_extension and the docker container, in the root of the 
repository run;

```bash
./utils/docker/build_image.sh
```

Once built, to connect to the container run;

```bash
./utils/docker/run_image.sh
```

When in the container, to print out information on the tests, or to run them, change directory to `tests/generic` 
and run;

```bash
# print out test titles
pysys.py print 

# print out full test details
pysys.py print -f

# run the tests against Obscuro testnet
pysys.py run 

# run the tests against Obscuro dev-testnet
pysys.py run -m obscuro.dev 

# run the tests against a local ganache network 
pysys.py run -m ganache

# print out test titles
pysys.py print 

# print out full test details
pysys.py print -f
```

To run the same tests against Ropsten, a `.username.properties` file should be created in the root of the working 
directory of the project (where `username` is the output of `echo $USER`), and the following properties should be added 
as based on details relevant to the user; 

```
[all]
Account1PK=<private key of account 1 available e.g. via metamask>
Account2PK=<private key of account 2>
Account3PK=<private key of account 3>
GameUserPK=<private key of account 4>

[ropsten]
ProjectID=<project ID>
```

These need to be real accounts to run on Ropsten, whereas for Ganache and Obscuro, currently default ones can be used 
as detailed in [.default.properties](./.default.properties). To run the tests against Ropsten use;

```bash
# run the tests against ropsten
pysys.py run -m ropsten
```









