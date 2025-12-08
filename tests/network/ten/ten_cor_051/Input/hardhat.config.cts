require("@nomicfoundation/hardhat-toolbox");
require("@tenprotocol/ten-hardhat-plugin");
require("hardhat-deploy");

const { PK1, PK2, CHAINID, HOST, PORT } = process.env;

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
      chainId: Number(CHAINID),
      url: `${HOST}:${PORT}/v1/`,
      useGateway: true,
      accounts: [ `0x${PK1}`, `0x${PK2}` ]
    }
  },
};

export default config;