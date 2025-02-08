import { ethers } from "hardhat";
import { saveContractAddress } from "../helpers/contractAddress";

async function main() {
    console.log("Deploying AIAgentNFT...");
    const AIAgentNFT = await ethers.getContractFactory("AIAgentNFT");
    const aiAgentNFT = await AIAgentNFT.deploy();

    await aiAgentNFT.waitForDeployment();
    
    const address = await aiAgentNFT.getAddress();
    console.log("AIAgentNFT deployed to:", address);

    // Save the address for frontend and other scripts
    saveContractAddress(address);
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });