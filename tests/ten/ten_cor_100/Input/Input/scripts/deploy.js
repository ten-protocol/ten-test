const { ethers, upgrades } = require("hardhat");

async function main() {
  const GameV1 = await ethers.getContractFactory("GameV1");
  const gamev1 = await upgrades.deployProxy(GameV1);
  await gamev1.waitForDeployment();
  const address = await gamev1.getAddress()
  console.log("Proxy deployed at", address);

  const GameV2 = await ethers.getContractFactory("GameV2");
  const gamev2 = await upgrades.upgradeProxy(address, GameV2);
  console.log("DoubleV2 deployed to:", await gamev2.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
