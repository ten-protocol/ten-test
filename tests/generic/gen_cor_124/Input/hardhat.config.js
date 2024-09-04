require("@nomicfoundation/hardhat-toolbox");
require("@openzeppelin/hardhat-upgrades");
require('console-stamp')(console, 'HH:MM:ss')

const { PK1, PK2, HOST, PORT, TOKEN } = process.env;

module.exports = {
  solidity:  "0.8.7",
  defaultNetwork: "ganache",
  networks: {
    ten: {
      chainId: 443,
      url: `${HOST}:${PORT}/v1/?token=${TOKEN}`,
      gasPrice: 2000000000,
      accounts: [ `0x${PK1}`, `0x${PK2}` ]
    },
    ganache: {
      chainId: 1337,
      url: `${HOST}:${PORT}`,
      accounts: [ `0x${PK1}`, `0x${PK2}` ],
      gasMultiplier: 2
    }
  }
};