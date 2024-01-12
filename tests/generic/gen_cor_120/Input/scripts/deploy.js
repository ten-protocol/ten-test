const hre = require("hardhat");

async function main() {
  const testMaths = await hre.ethers.deployContract("TestMath");
  await testMaths.waitForDeployment();
  console.log("TestMaths deployed at", testMaths.target);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
