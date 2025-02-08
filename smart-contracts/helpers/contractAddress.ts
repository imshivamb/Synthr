import fs from 'fs';
import path from 'path';

const CONTRACT_ADDRESS_FILE = path.join(__dirname, '../../frontend/.env.local');

export function saveContractAddress(address: string) {
    const envContent = `NEXT_PUBLIC_LOCAL_CONTRACT_ADDRESS=${address}`;
    fs.writeFileSync(CONTRACT_ADDRESS_FILE, envContent);
    console.log('Contract address saved to frontend/.env.local');
}

export function getContractAddress(): string {
    try {
        if (!fs.existsSync(CONTRACT_ADDRESS_FILE)) {
            throw new Error('Contract address file not found');
        }
        const content = fs.readFileSync(CONTRACT_ADDRESS_FILE, 'utf8');
        const match = content.match(/NEXT_PUBLIC_LOCAL_CONTRACT_ADDRESS=(.*)/);
        return match ? match[1] : '';
    } catch (error) {
        console.error('Error reading contract address:', error);
        return '';
    }
}