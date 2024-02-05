# Hardhat project to deploy a sample (single) contract

Created as described [here](https://hardhat.org/tutorial/creating-a-new-hardhat-project) i.e. the project was initially 
created using the below commands;

```shell
npm init
npm install --save hardhat
npm install --save dotenv
npx hardhat init
```

### Running to deploy the contract

The hardhat config JS file reads relevant variables from a `.env` file in the project root which should have the following contents;

```shell
APP_DEV_PK=<account private key>
TEN_TOKEN=<token from the gateway>
```

The config is setup to allow deployment to a live network as described [here](https://hardhat.org/tutorial/deploying-to-a-live-network)
 meaning you can run the below to start up and deploy either to hardhat, or to deploy to TEN testnet once started. 

```shell
# start a hardhat network and deploy 
npx hardhat node
npx hardhat run scripts/deploy.js

# deploy to ten testnet 
npx hardhat run --network ten scripts/deploy.js
```



