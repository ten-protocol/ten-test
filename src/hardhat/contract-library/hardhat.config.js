require("@nomicfoundation/hardhat-toolbox");
require('dotenv').config();

const { APP_DEV_PK, TEN_TOKEN } = process.env;

module.exports = {
  solidity:  "0.8.7",
  defaultNetwork: "hardhat",
  networks: {
    ten: {
      deploy: [ "scripts/" ],
      chainId: 443,
      url: `https://testnet.obscu.ro/v1/${TEN_TOKEN}`,
      gasPrice: 2000000000,
      accounts: [ `0x${APP_DEV_PK}` ]
    },
    ten_local: {
      deploy: [ "scripts/" ],
      chainId: 443,
      url: `http://127.0.0.1:3000/v1/${TEN_TOKEN}`,
      gasPrice: 2000000000,
      accounts: [ `0x${APP_DEV_PK}` ]
    },
    hardhat: {
      deploy: [ "scripts/" ],
      chainId: 1337,
      accounts: [
        { "privateKey": `0x${APP_DEV_PK}`,  "balance": "174165200000000000" }
      ]
    }
  }
};