
const hre = require("hardhat");

async function main() {
  const MathUtils = await hre.ethers.getContractFactory("MathUtils");
  const mathUtils = await MathUtils.deploy();
  MathUtils_ADDRESS = mathUtils.target;
  console.log("Library MathUtils deployed at", MathUtils_ADDRESS);

  const TestMaths = await hre.ethers.getContractFactory("TestMath", {
    libraries: {
      MathUtils: MathUtils_ADDRESS,
    },
  });

  const testMaths = await TestMaths.deploy();
  TestMaths_ADDRESS = testMaths.target;
  console.log("TestUtils deployed at", TestMaths_ADDRESS);
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
