import { createPublicClient, http } from 'viem'
import { hardhat } from 'viem/chains'
import { CONTRACT_ADDRESS, CONTRACT_ABI } from '@/config/contracts'

export function useContract() {
    if (!CONTRACT_ADDRESS) {
        throw new Error('Contract address not found')
    }

    const client = createPublicClient({
        chain: hardhat,
        transport: http()
    })

    return {
        address: CONTRACT_ADDRESS as `0x${string}`,
        abi: CONTRACT_ABI,
        client
    }
}