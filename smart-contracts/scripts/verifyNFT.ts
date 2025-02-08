// scripts/verifyNFT.ts
import { ethers } from "hardhat";
import { AIAgentNFT } from "../typechain-types";
import { getContractAddress } from "../helpers/contractAddress";

async function main() {
    try {
        const CONTRACT_ADDRESS = getContractAddress();
        const TOKEN_ID = 0; // First minted token has ID 0

        // Get the deployer's address
        const [owner] = await ethers.getSigners();

        // Get the deployed contract instance
        const contract = await ethers.getContractAt("AIAgentNFT", CONTRACT_ADDRESS, owner);
        console.log("Verifying NFT at contract:", CONTRACT_ADDRESS);

        // Get token information
        const tokenOwner = await contract.ownerOf(TOKEN_ID);
        const tokenURI = await contract.tokenURI(TOKEN_ID);

        console.log("\nNFT Verification Results:");
        console.log("------------------------");
        console.log("Contract Address:", CONTRACT_ADDRESS);
        console.log("Token ID:", TOKEN_ID);
        console.log("Owner:", tokenOwner);
        console.log("Token URI:", tokenURI);
        console.log("IPFS Gateway URL:", tokenURI.replace("ipfs://", "https://gateway.pinata.cloud/ipfs/"));
        
        console.log("\nOwnership Verification:");
        console.log("------------------------");
        console.log("Expected Owner:", owner.address);
        console.log("Actual Owner:", tokenOwner);
        console.log("Ownership Verified:", owner.address === tokenOwner);

    } catch (error: any) {
        console.error("Error verifying NFT:", error.message);
        if (error.message.includes("nonexistent token")) {
            console.log("\nToken might not be minted yet at this address");
        }
        throw error;
    }
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });