from typing import List, Dict, Any, Optional, Callable
from web3 import Web3
from web3.contract import Contract
from app.core.config import settings

class BlockchainEventService:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.RPC_URL))
        self.contract = self._init_contract()
        self._event_handlers: Dict[str, List[Callable]] = {}
        
    def _init_contract(self) -> Contract:
        """Initialise a contract instance."""
        return self.w3.eth.contract(address=settings.CONTRACT_ADDRESS, abi=settings.CONTRACT_ABI)
    
    async def get_event_logs(
        self,
        event_name: str,
        from_block: int,
        to_block: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get past events of specific type"""
        if to_block is None:
            to_block = await self.w3.eth.block_number

        event = getattr(self.contract.events, event_name)
        events = await event.get_logs(
            fromBlock=from_block,
            toBlock=to_block
        )
        
        return [dict(evt) for evt in events]
    
    async def get_mint_events(
        self,
        from_block: int,
        to_block: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get agent mint events"""
        return await self.get_event_logs('AgentMinted', from_block, to_block)

    async def get_transfer_events(
        self,
        from_block: int,
        to_block: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get agent transfer events"""
        return await self.get_event_logs('Transfer', from_block, to_block)
    
    async def get_listing_events(
        self,
        from_block: int,
        to_block: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get agent listing events"""
        return await self.get_event_logs('AgentListed', from_block, to_block)

    async def get_purchase_events(
        self,
        from_block: int,
        to_block: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get agent purchase events"""
        return await self.get_event_logs('AgentPurchased', from_block, to_block)

    def subscribe_to_event(
        self,
        event_name: str,
        callback: Callable[[Dict[str, Any]], None]
    ) -> None:
        """Subscribe to contract events"""
        if event_name not in self._event_handlers:
            self._event_handlers[event_name] = []
        self._event_handlers[event_name].append(callback)

        event = getattr(self.contract.events, event_name)
        event.create_filter(fromBlock='latest').watch(callback)

    def unsubscribe_from_event(
        self,
        event_name: str,
        callback: Callable[[Dict[str, Any]], None]
    ) -> None:
        """Unsubscribe from contract events"""
        if event_name in self._event_handlers:
            self._event_handlers[event_name].remove(callback)

    async def get_transaction_receipt(
        self,
        tx_hash: str
    ) -> Dict[str, Any]:
        """Get transaction receipt"""
        receipt = await self.w3.eth.get_transaction_receipt(tx_hash)
        return dict(receipt)

    async def wait_for_transaction(
        self,
        tx_hash: str,
        timeout: int = 120,
        poll_interval: float = 0.1
    ) -> Dict[str, Any]:
        """Wait for transaction to be mined"""
        receipt = await self.w3.eth.wait_for_transaction_receipt(
            tx_hash,
            timeout=timeout,
            poll_latency=poll_interval
        )
        return dict(receipt)

events_service = BlockchainEventService()