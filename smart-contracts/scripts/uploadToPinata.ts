// scripts/uploadToPinata.ts
import PinataClient from '@pinata/sdk';
import dotenv from 'dotenv';
import fs from 'fs';

dotenv.config();

const PINATA_API_KEY = process.env.PINATA_API_KEY;
const PINATA_SECRET_KEY = process.env.PINATA_SECRET_KEY;

interface Metadata {
    name: string;
    description: string;
    image?: string;
    properties: {
        capabilities: string[];
        version: string;
        modelType: string;
    };
}

async function uploadToPinata() {
    if (!PINATA_API_KEY || !PINATA_SECRET_KEY) {
        throw new Error('Pinata credentials are required in .env file');
    }

    try {
        console.log('Initializing Pinata client...');
        const pinata = new PinataClient(PINATA_API_KEY, PINATA_SECRET_KEY);

        // Test connection
        const testResult = await pinata.testAuthentication();
        console.log('Authentication test:', testResult);

        // Create metadata
        const metadata: Metadata = {
            name: "Basic AI Agent",
            description: "A test AI agent",
            properties: {
                capabilities: ["code completion", "bug detection"],
                version: "1.0.0",
                modelType: "gpt-2"
            }
        };

        // Create a simple SVG for preview
        const svgContent = `
            <svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
                <rect width="100" height="100" fill="blue"/>
                <text x="50" y="50" text-anchor="middle" fill="white">AI Agent</text>
            </svg>
        `;

        // Save SVG temporarily
        const tempFilePath = 'temp_preview.svg';
        fs.writeFileSync(tempFilePath, svgContent);

        console.log('Uploading preview image...');
        const readableStream = fs.createReadStream(tempFilePath);
        
        // File upload options with correct types
        const imageOptions = {
            pinataMetadata: {
                name: 'ai-agent-preview.svg'
            }
        };

        const imageResult = await pinata.pinFileToIPFS(readableStream, imageOptions);

        // Add image URL to metadata
        metadata.image = `ipfs://${imageResult.IpfsHash}`;

        console.log('Uploading metadata...');
        // JSON upload options with correct types
        const jsonOptions = {
            pinataMetadata: {
                name: 'ai-agent-metadata.json'
            }
        };

        const result = await pinata.pinJSONToIPFS(metadata, jsonOptions);

        // Clean up temp file
        fs.unlinkSync(tempFilePath);

        console.log('Upload successful!');
        console.log('Metadata IPFS Hash:', result.IpfsHash);
        console.log('Preview Image IPFS Hash:', imageResult.IpfsHash);
        console.log('Metadata URL:', `ipfs://${result.IpfsHash}`);
        console.log('Gateway URLs:');
        console.log('- Metadata:', `https://gateway.pinata.cloud/ipfs/${result.IpfsHash}`);
        console.log('- Image:', `https://gateway.pinata.cloud/ipfs/${imageResult.IpfsHash}`);

        return {
            metadataUrl: `ipfs://${result.IpfsHash}`,
            imageUrl: `ipfs://${imageResult.IpfsHash}`,
            metadataHash: result.IpfsHash,
            imageHash: imageResult.IpfsHash
        };
    } catch (error: any) {
        console.error('Upload failed:', {
            message: error.message,
            details: error
        });
        throw error;
    }
}

// Execute the upload
uploadToPinata()
    .then((result) => {
        console.log('Process completed successfully');
        console.log('Results:', result);
        process.exit(0);
    })
    .catch((error) => {
        console.error('Process failed:', error.message);
        process.exit(1);
    });