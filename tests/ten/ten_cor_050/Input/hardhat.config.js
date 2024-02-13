require("@nomicfoundation/hardhat-toolbox");
require("ten-hardhat-plugin")

const { PK, HOST, PORT } = process.env;

module.exports = {
  solidity:  "0.8.19",
  defaultNetwork: "ten",
  networks: {
    ten: {
      deploy: [ "scripts/" ],
      chainId: 443,
      url: `${HOST}:${PORT}/v1/`,
      useGateway: true,
      gasPrice: 2000000000,
      accounts: [ `0x${PK}` ]
    }
  }
};