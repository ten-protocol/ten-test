Market (PUMP) E2E Tests
-----------------------

To run you will need to run the market application in hardhat. The `market` repo should be cloned into the same parent 
directory as `ten-test` so they are sibling directories. In order for the `AAVE` vault to be used as a test vault, the 
following environment argument should be set.

```bash
export USE_AAVE_VAULT = false
```

In the `market` directory, to then start up the application, in two separate terminals use;

```bash
yarn chain                     # terminal 1
yarn deploy --network local    # terminal 2
```

The first command starts up a hardhat network. The second builds and deploys the application. To run the tests you must 
build the artifacts using the `get_artifacts.sh` script located in the root of the `ten-test` project. The `ten-test` 
repo should be set up as described in the top level README.md of the project. 