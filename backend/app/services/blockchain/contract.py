from typing import Dict, Any, Optional, List
from decimal import Decimal
from web3 import Web3
from eth_typing import Address
from web3.contract import Contract
from web3.exceptions import ContractLogicError

from app.core.config import settings
from app.models.agent import Agent

class ContractService:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.RPC_URL))
        self.contract = self._init_contract()

    def _init_contract(self) -> Contract:
        """Initialize contract instance"""
        return self.w3.eth.contract(
            address=settings.CONTRACT_ADDRESS,
            abi=settings.CONTRACT_ABI
        )

    # Basic Token Functions
    async def get_token_uri(self, token_id: int) -> str:
        """Get token URI for an agent"""
        return await self.contract.functions.tokenURI(token_id).call()

    async def get_owner(self, token_id: int) -> str:
        """Get owner address of token"""
        return await self.contract.functions.ownerOf(token_id).call()

    async def get_listing_price(self, token_id: int) -> Decimal:
        """Get listing price of token"""
        wei_price = await self.contract.functions.getPrice(token_id).call()
        return Decimal(self.w3.from_wei(wei_price, 'ether'))

    async def is_token_listed(self, token_id: int) -> bool:
        """Check if token is listed for sale"""
        return await self.contract.functions.isListed(token_id).call()

    # Advanced Token Functions
    async def get_token_royalty_info(self, token_id: int, sale_price: Decimal) -> Dict[str, Any]:
        """Get royalty information for token"""
        wei_price = self.w3.to_wei(sale_price, 'ether')
        receiver, royalty_amount = await self.contract.functions.royaltyInfo(
            token_id, 
            wei_price
        ).call()
        return {
            'receiver': receiver,
            'amount': Decimal(self.w3.from_wei(royalty_amount, 'ether'))
        }

    async def get_token_history(self, token_id: int) -> List[Dict[str, Any]]:
        """Get complete transaction history for a token"""
        transfer_events = await self.contract.events.Transfer.get_logs(
            fromBlock=0,
            argument_filters={'tokenId': token_id}
        )
        return [dict(evt) for evt in transfer_events]

    # Transaction Functions
    async def mint_agent(
        self,
        owner_address: str,
        token_uri: str,
        private_key: str,
        royalty_percentage: Optional[int] = None
    ) -> Dict[str, Any]:
        """Mint new agent NFT with optional royalty"""
        nonce = await self.w3.eth.get_transaction_count(owner_address)
        
        # Build mint function
        if royalty_percentage is not None:
            transaction = await self.contract.functions.mintAgentWithRoyalty(
                owner_address,
                token_uri,
                royalty_percentage
            ).build_transaction({
                'chainId': settings.CHAIN_ID,
                'gas': 2000000,
                'gasPrice': await self.w3.eth.gas_price,
                'nonce': nonce,
            })
        else:
            transaction = await self.contract.functions.mintAgent(
                owner_address,
                token_uri
            ).build_transaction({
                'chainId': settings.CHAIN_ID,
                'gas': 2000000,
                'gasPrice': await self.w3.eth.gas_price,
                'nonce': nonce,
            })
        
        signed_txn = self.w3.eth.account.sign_transaction(
            transaction,
            private_key=private_key
        )
        
        tx_hash = await self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        receipt = await self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return dict(receipt)

    async def list_agent(
        self,
        token_id: int,
        price: Decimal,
        owner_address: str,
        private_key: str
    ) -> Dict[str, Any]:
        """List agent for sale"""
        price_wei = self.w3.to_wei(price, 'ether')
        nonce = await self.w3.eth.get_transaction_count(owner_address)
        
        transaction = await self.contract.functions.listAgent(
            token_id,
            price_wei
        ).build_transaction({
            'chainId': settings.CHAIN_ID,
            'gas': 2000000,
            'gasPrice': await self.w3.eth.gas_price,
            'nonce': nonce,
        })
        
        signed_txn = self.w3.eth.account.sign_transaction(
            transaction,
            private_key=private_key
        )
        
        tx_hash = await self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        receipt = await self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return dict(receipt)

    async def delist_agent(
        self,
        token_id: int,
        owner_address: str,
        private_key: str
    ) -> Dict[str, Any]:
        """Remove agent from sale"""
        nonce = await self.w3.eth.get_transaction_count(owner_address)
        
        transaction = await self.contract.functions.delistAgent(
            token_id
        ).build_transaction({
            'chainId': settings.CHAIN_ID,
            'gas': 2000000,
            'gasPrice': await self.w3.eth.gas_price,
            'nonce': nonce,
        })
        
        signed_txn = self.w3.eth.account.sign_transaction(
            transaction,
            private_key=private_key
        )
        
        tx_hash = await self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        receipt = await self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return dict(receipt)

    async def buy_agent(
        self,
        token_id: int,
        price: Decimal,
        buyer_address: str,
        private_key: str
    ) -> Dict[str, Any]:
        """Buy agent"""
        price_wei = self.w3.to_wei(price, 'ether')
        nonce = await self.w3.eth.get_transaction_count(buyer_address)
        
        transaction = await self.contract.functions.purchaseAgent(
            token_id
        ).build_transaction({
            'chainId': settings.CHAIN_ID,
            'gas': 2000000,
            'gasPrice': await self.w3.eth.gas_price,
            'nonce': nonce,
            'value': price_wei
        })
        
        signed_txn = self.w3.eth.account.sign_transaction(
            transaction,
            private_key=private_key
        )
        
        tx_hash = await self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        receipt = await self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return dict(receipt)

    # Batch Operations
    async def batch_mint_agents(
        self,
        owner_address: str,
        token_uris: List[str],
        private_key: str
    ) -> List[Dict[str, Any]]:
        """Mint multiple agents in one transaction"""
        nonce = await self.w3.eth.get_transaction_count(owner_address)
        
        transaction = await self.contract.functions.batchMintAgents(
            owner_address,
            token_uris
        ).build_transaction({
            'chainId': settings.CHAIN_ID,
            'gas': 5000000,  # Higher gas limit for batch operation
            'gasPrice': await self.w3.eth.gas_price,
            'nonce': nonce,
        })
        
        signed_txn = self.w3.eth.account.sign_transaction(
            transaction,
            private_key=private_key
        )
        
        tx_hash = await self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        receipt = await self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return dict(receipt)

    # Query Functions
    async def get_token_info(self, token_id: int) -> Dict[str, Any]:
        """Get comprehensive token information"""
        try:
            owner = await self.get_owner(token_id)
            is_listed = await self.is_token_listed(token_id)
            
            info = {
                'token_id': token_id,
                'owner': owner,
                'uri': await self.get_token_uri(token_id),
                'is_listed': is_listed,
            }
            
            if is_listed:
                info['price'] = await self.get_listing_price(token_id)
            
            # Get royalty info for a sample price of 1 ETH
            royalty_info = await self.get_token_royalty_info(token_id, Decimal('1.0'))
            info['royalty'] = royalty_info
            
            return info
        except ContractLogicError:
            return None

    async def get_total_supply(self) -> int:
        """Get total number of minted tokens"""
        return await self.contract.functions.totalSupply().call()

    async def get_tokens_of_owner(self, owner_address: str) -> List[Dict[str, Any]]:
        """Get detailed information about all tokens owned by address"""
        balance = await self.contract.functions.balanceOf(owner_address).call()
        tokens = []
        
        for i in range(balance):
            token_id = await self.contract.functions.tokenOfOwnerByIndex(
                owner_address, 
                i
            ).call()
            token_info = await self.get_token_info(token_id)
            if token_info:
                tokens.append(token_info)
        
        return tokens

    # Market Analysis
    async def get_market_stats(self) -> Dict[str, Any]:
        """Get marketplace statistics"""
        total_supply = await self.get_total_supply()
        listed_count = 0
        total_value = Decimal('0')
        
        for token_id in range(total_supply):
            try:
                is_listed = await self.is_token_listed(token_id)
                if is_listed:
                    listed_count += 1
                    price = await self.get_listing_price(token_id)
                    total_value += price
            except ContractLogicError:
                continue
        
        return {
            'total_supply': total_supply,
            'listed_count': listed_count,
            'total_value': total_value,
            'avg_price': total_value / listed_count if listed_count > 0 else Decimal('0')
        }

contract_service = ContractService()