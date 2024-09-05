const { ethers, upgrades } = require("hardhat");

async function main() {
  const DoubleV1 = await ethers.getContractFactory("DoubleV1");
  const doublev1 = await DoubleV1.deploy();
  await doublev1.waitForDeployment();
  console.log("DoubleV1 deployed to:", beacon.address);

  const UpgradeableBeacon = await ethers.getContractFactory("UpgradeableBeacon");
  const beacon = await UpgradeableBeacon.deploy(logicV1.address);
  await beacon.waitForDeployment();
  console.log("Beacon deployed to:", beacon.address);

  const BeaconProxy = await ethers.getContractFactory("BeaconProxy");
  const proxy = await BeaconProxy.deploy(beacon.address, []);
  await proxy.waitForDeployment();
  console.log("Proxy deployed to:", proxy.address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
