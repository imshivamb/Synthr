import { useContract } from '@/hooks/useContract';
import { createMarketplaceService } from '@/services/marketplace';

export function useMarketplaceService() {
  const { address, abi, client } = useContract();
  const contract = { address, abi };
  
  return createMarketplaceService(contract, client);
}