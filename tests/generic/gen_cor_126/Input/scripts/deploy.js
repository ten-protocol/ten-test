const { ethers, upgrades } = require("hardhat");

async function main() {
  // deploy the implementation contract
  const DoubleV1 = await ethers.getContractFactory("DoubleV1");
  const doublev1 = await DoubleV1.deploy();
  await doublev1.waitForDeployment();
  console.log("DoubleV1 deployed at", doublev1.target);

  // deploy the upgradable beacon which contains the address of the implementation contract
  const UpgradeableBeacon = await ethers.getContractFactory("UpgradeableBeacon");
  const beacon = await UpgradeableBeacon.deploy(doublev1.target);
  await beacon.waitForDeployment();
  console.log("Beacon deployed at", beacon.target);

  // deploy the proxy that will get the implementation address from the beacon
  const BeaconProxy = await ethers.getContractFactory("BeaconProxy");
  const proxy = await BeaconProxy.deploy(beacon.target, "0x");
  await proxy.waitForDeployment();
  console.log("Proxy deployed at", proxy.target);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
