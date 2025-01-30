# Local Development Setup Guide

## Initial Setup 🚀

### 1. Clone & Install
```bash
# Clone repository
git clone https://github.com/yourusername/ai-agent-marketplace.git
cd ai-agent-marketplace

# Install root dependencies
npm install

# Setup smart contracts
cd smart-contracts
npm install
npx hardhat compile

# Setup frontend
cd ../frontend
npm install

# Setup backend
cd ../backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

### 2. Environment Setup

#### Smart Contracts (.env)
```env
PRIVATE_KEY=your_private_key
ETHERSCAN_API_KEY=your_etherscan_key
NFT_STORAGE_KEY=your_nft_storage_key
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_CONTRACT_ADDRESS=your_contract_address
NEXT_PUBLIC_RPC_URL=your_rpc_url
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379
NFT_STORAGE_KEY=your_nft_storage_key
```

### 3. Database Setup
```bash
# Start PostgreSQL (if using Docker)
docker-compose up -d db

# Run migrations
cd backend
alembic upgrade head
```

## Running the Project 🏃‍♂️

### 1. Start Blockchain
```bash
cd smart-contracts
npx hardhat node
```

### 2. Deploy Contracts (New Terminal)
```bash
cd smart-contracts
npx hardhat run scripts/deploy.ts --network localhost
```

### 3. Start Backend (New Terminal)
```bash
cd backend
uvicorn main:app --reload
```

### 4. Start Frontend (New Terminal)
```bash
cd frontend
npm run dev
```

## Development Workflow 💻

### Smart Contract Development
1. Make changes in `contracts/`
2. Run tests: `npx hardhat test`
3. Deploy locally: `npx hardhat run scripts/deploy.ts --network localhost`

### Frontend Development
1. Make changes in `frontend/`
2. Run tests: `npm test`
3. Check formatting: `npm run lint`

### Backend Development
1. Make changes in `backend/`
2. Run tests: `pytest`
3. Update API docs: `python scripts/generate_openapi.py`

## Testing 🧪

### Run All Tests
```bash
# Smart Contracts
cd smart-contracts
npx hardhat test

# Frontend
cd frontend
npm test

# Backend
cd backend
pytest
```

## Common Issues & Solutions 🔧

### Smart Contract Issues
1. Network Issues
   ```bash
   # Reset Hardhat Network
   npx hardhat clean
   npx hardhat node
   ```

2. Contract Deployment Fails
   ```bash
   # Check network configuration
   cat hardhat.config.ts
   ```

### Frontend Issues
1. Wallet Connection
   ```bash
   # Check MetaMask network
   # Should match hardhat network ID
   ```

2. Contract Interaction
   ```bash
   # Verify contract address in .env.local
   # Check ABI generation
   ```

### Backend Issues
1. Database Connection
   ```bash
   # Check PostgreSQL service
   docker-compose ps
   ```

2. Redis Connection
   ```bash
   # Verify Redis service
   redis-cli ping
   ```