interface NetworkConfig {
    name: string;
    chainId: number;
    aiAgentNFTAddress: string;
    rpcUrl: string;
}

const networks: { [key: string]: NetworkConfig } = {
    localhost: {
        name: 'Hardhat Local',
        chainId: 31337,
        aiAgentNFTAddress: process.env.NEXT_PUBLIC_LOCAL_CONTRACT_ADDRESS || '',
        rpcUrl: 'http://127.0.0.1:8545'
    }
}

export const currentNetwork = networks.localhost;

export const CONTRACT_ADDRESS = currentNetwork.aiAgentNFTAddress;
export const CHAIN_ID = currentNetwork.chainId;


import { abi as AIAgentNFTABI } from '../../../smart-contracts/artifacts/contracts/AIAgentNFT.sol/AIAgentNFT.json';

export const CONTRACT_ABI = AIAgentNFTABI;