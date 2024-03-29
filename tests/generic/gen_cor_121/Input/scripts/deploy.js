const { ethers } = require("hardhat");

async function main() {
  const utilsFactory = await ethers.getContractFactory("MathUtils");
  const utilsInstance = await utilsFactory.deploy();
  await utilsInstance.waitForDeployment();
  console.log("Library MathUtils deployed at", utilsInstance.target);

  const mathsFactory = await ethers.getContractFactory("TestMath", {
    libraries: {
      MathUtils: utilsInstance.target,
    },
  });

  const mathsInstance = await mathsFactory.deploy();
  await mathsInstance.waitForDeployment();
  console.log("TestMaths deployed at", mathsInstance.target);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
