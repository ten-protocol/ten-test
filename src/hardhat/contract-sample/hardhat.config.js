require("@nomicfoundation/hardhat-toolbox");
require('dotenv').config();

const { APP_DEV_PK, TEN_TOKEN } = process.env;

module.exports = {
  solidity:  "0.8.7",
  defaultNetwork: "ten",
  networks: {
    ten: {
      deploy: [ "scripts/" ],
      chainId: 443,
      url: `https://127.0.0.1:3000/v1/${TEN_TOKEN}`,
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