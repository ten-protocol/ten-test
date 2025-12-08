const { ethers, upgrades } = require("hardhat");

async function main() {
  const address = process.env.ADDRESS;
  console.log("Proxy address passed to main:", address);

  const GameV2 = await ethers.getContractFactory("GameV2");
  const gameV2 = await upgrades.upgradeProxy(address, GameV2);
  console.log("GameV2 deployed to:", await gameV2.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
