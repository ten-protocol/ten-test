require("@nomicfoundation/hardhat-toolbox");
require("ten-hardhat-plugin");
require("hardhat-deploy");

const { PK1, PK2, PK3, HOST, PORT } = process.env;

const config: HardhatUserConfig = {
  solidity: "0.8.17",
  defaultNetwork: "ten",
  namedAccounts: {
    app_developer1: {
      default: 0,
    },
    app_developer2: {
      default: 1,
    },
  },
  networks: {
    ten: {
      deploy: [ "scripts/" ],
      chainId: 443,
      url: `${HOST}:${PORT}/v1/`,
      useGateway: true,
      accounts: [ `0x${PK1}`, `0x${PK2}`, `0x${PK3}` ]
    }
  },
};

export default config;