import { ethers } from "hardhat";

async function main() {
  // Get the ContractFactory
  const AIAgentNFT = await ethers.getContractFactory("AIAgentNFT");

  // Deploy the contract
  console.log("Deploying AIAgentNFT...");
  const aiAgentNFT = await AIAgentNFT.deploy();
  
  // Wait for deployment to complete
  await aiAgentNFT.waitForDeployment();

  // Get the deployed contract address
  const deployedAddress = await aiAgentNFT.getAddress();
  console.log(`AIAgentNFT deployed to: ${deployedAddress}`);
}

// Handle errors
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});