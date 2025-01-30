import { ethers } from "hardhat";

// Use the values from your successful IPFS upload
const METADATA_URL = "ipfs://QmfUqvbHzMh8JgRWaSGTftcUKE1GGKB9vhTpGPY5iaZjS1";
const CONTRACT_ADDRESS = "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512";

async function main() {
    try {
        // Get the AIAgentNFT contract factory
        const AIAgentNFT = await ethers.getContractFactory("AIAgentNFT");

        
        // Get the deployer's address
        const [owner] = await ethers.getSigners();
        console.log("Minting from address:", await owner.getAddress());

        // Get the deployed contract instance
        const contract = await ethers.getContractAt("AIAgentNFT", CONTRACT_ADDRESS, owner);

        console.log("Contract attached at:", CONTRACT_ADDRESS);

        // Mint the NFT
        console.log("Minting NFT with metadata:", METADATA_URL);
        const tx = await contract.connect(owner).mintAgent(await owner.getAddress(), METADATA_URL);
        
        console.log("Waiting for transaction confirmation...");
        const receipt = await tx.wait();
        if (!receipt) {
            throw new Error("Transaction receipt is null. Minting may have failed.");
        }


        // Log the results
        console.log("NFT Minted Successfully!");
        console.log({
            transactionHash: receipt.hash,
            contractAddress: CONTRACT_ADDRESS,
            owner: await owner.getAddress(),
            metadataUrl: METADATA_URL
        });

    } catch (error) {
        console.error("Error minting NFT:", error);
        throw error;
    }
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });