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
  console.log("TestMaths deployed at", TestMaths_ADDRESS);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
