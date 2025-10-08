const { ethers, upgrades } = require("hardhat");

async function main() {
  const GameV1 = await ethers.getContractFactory("GameV1");
  const gamev1 = await upgrades.deployProxy(GameV1);
  await gamev1.waitForDeployment();
  const address = await gamev1.getAddress()
  console.log("Proxy deployed at", address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
