const { ethers, upgrades } = require("hardhat");

async function main() {
  const IncrementerV1 = await ethers.getContractFactory("IncrementerV1");
  const incrementerV1 = await upgrades.deployProxy(IncrementerV1);
  await incrementerV1.waitForDeployment();
  const address = await incrementerV1.getAddress()
  console.log("Incrementer V1 deployed to:", address);

  const IncrementerV2 = await ethers.getContractFactory("IncrementerV2");
  let incrementerV2 = await upgrades.upgradeProxy(address, IncrementerV2);
  console.log("Incrementer V2 deployed to:", await incrementerV2.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
