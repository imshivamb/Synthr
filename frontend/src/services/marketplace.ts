import { AIAgent, MarketplaceFilters } from '@/types/marketplace';
import { parseEther } from 'viem';

export const createMarketplaceService = (contract: any, client: any) => {
  // Fetch all agents from contract
  const fetchAgentsFromContract = async (): Promise<AIAgent[]> => {
    try {
      // Get total supply of agents
      const totalSupply = await contract.read.totalSupply();
      const agents: AIAgent[] = [];

      // Fetch each agent
      for (let i = 0; i < totalSupply; i++) {
        const tokenId = await contract.read.tokenByIndex(i);
        const agent = await getAgentDetails(tokenId.toString());
        agents.push(agent);
      }

      return agents;
    } catch (error) {
      console.error('Error fetching from contract:', error);
      throw new Error('Failed to fetch agents from contract');
    }
  };

  // Get single agent details
  const getAgentDetails = async (tokenId: string): Promise<AIAgent> => {
    try {
      // Get token URI and metadata
      const tokenURI = await contract.read.tokenURI(tokenId);
      const response = await fetch(tokenURI);
      if (!response.ok) throw new Error('Failed to fetch metadata');
      const metadata = await response.json();

      // Get owner/creator info
      const owner = await contract.read.ownerOf(tokenId);
      const isListed = await contract.read.isListed(tokenId);
      const price = isListed ? await contract.read.getPrice(tokenId) : '0';

      return {
        id: tokenId,
        tokenId: tokenId,
        name: metadata.name,
        description: metadata.description,
        image: metadata.image,
        price: price.toString(),
        creator: {
          address: owner,
          name: metadata.creator_name
        },
        category: metadata.category,
        capabilities: metadata.capabilities,
        metadata: {
          modelType: metadata.model_type,
          version: metadata.version,
          created: metadata.created_at,
          updated: metadata.updated_at,
          stats: {
            uses: metadata.stats.uses,
            ratings: metadata.stats.ratings,
            averageRating: metadata.stats.average_rating
          }
        }
      };
    } catch (error) {
      console.error('Error fetching agent details:', error);
      throw new Error('Failed to fetch agent details');
    }
  };

  // Get user's owned agents
  const getUserAgents = async (address: string): Promise<AIAgent[]> => {
    try {
      const balance = await contract.read.balanceOf(address);
      const agents: AIAgent[] = [];

      for (let i = 0; i < balance; i++) {
        const tokenId = await contract.read.tokenOfOwnerByIndex(address, i);
        const agent = await getAgentDetails(tokenId.toString());
        agents.push(agent);
      }

      return agents;
    } catch (error) {
      console.error('Error fetching user agents:', error);
      throw new Error('Failed to fetch user agents');
    }
  };

  // Buy an agent
  const buyAgent = async (agentId: string, price: string): Promise<boolean> => {
    try {
      const transaction = await contract.write.purchaseAgent(
        [agentId],
        { value: parseEther(price) }
      );

      const receipt = await transaction.wait();
      return receipt.status === 1;
    } catch (error) {
      console.error('Error buying agent:', error);
      throw new Error('Failed to purchase agent');
    }
  };

  // List agent for sale
  const listAgent = async (agentId: string, price: string): Promise<boolean> => {
    try {
      const transaction = await contract.write.listAgent(
        [agentId, parseEther(price)]
      );

      const receipt = await transaction.wait();
      return receipt.status === 1;
    } catch (error) {
      console.error('Error listing agent:', error);
      throw new Error('Failed to list agent');
    }
  };

  // Delist agent from sale
  const delistAgent = async (agentId: string): Promise<boolean> => {
    try {
      const transaction = await contract.write.delistAgent([agentId]);
      const receipt = await transaction.wait();
      return receipt.status === 1;
    } catch (error) {
      console.error('Error delisting agent:', error);
      throw new Error('Failed to delist agent');
    }
  };

  // Update agent price
  const updateAgentPrice = async (agentId: string, newPrice: string): Promise<boolean> => {
    try {
      const transaction = await contract.write.updatePrice(
        [agentId, parseEther(newPrice)]
      );

      const receipt = await transaction.wait();
      return receipt.status === 1;
    } catch (error) {
      console.error('Error updating agent price:', error);
      throw new Error('Failed to update agent price');
    }
  };

  // Get agents with filters
  const getAgents = async (filters: MarketplaceFilters): Promise<AIAgent[]> => {
    try {
      const agents = await fetchAgentsFromContract();
      return applyFilters(agents, filters);
    } catch (error) {
      console.error('Error fetching agents:', error);
      throw new Error('Failed to fetch agents');
    }
  };

  // Apply filters to agents
  const applyFilters = (agents: AIAgent[], filters: MarketplaceFilters): AIAgent[] => {
    let filteredAgents = [...agents];

    // Apply search filter
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filteredAgents = filteredAgents.filter(agent =>
        agent.name.toLowerCase().includes(searchLower) ||
        agent.description.toLowerCase().includes(searchLower)
      );
    }

    // Apply category filter
    if (filters.category !== 'All') {
      filteredAgents = filteredAgents.filter(agent =>
        agent.category === filters.category
      );
    }

    // Apply price range filter
    filteredAgents = filteredAgents.filter(agent => {
      const price = parseFloat(agent.price);
      return price >= filters.priceRange.min && price <= filters.priceRange.max;
    });

    // Apply sorting
    switch (filters.sortBy) {
      case 'price-low':
        filteredAgents.sort((a, b) => parseFloat(a.price) - parseFloat(b.price));
        break;
      case 'price-high':
        filteredAgents.sort((a, b) => parseFloat(b.price) - parseFloat(a.price));
        break;
      case 'popular':
        filteredAgents.sort((a, b) => b.metadata.stats.ratings - a.metadata.stats.ratings);
        break;
      case 'latest':
      default:
        filteredAgents.sort((a, b) => 
          new Date(b.metadata.created).getTime() - new Date(a.metadata.created).getTime()
        );
    }

    return filteredAgents;
  };

  // Return all service functions
  return {
    getAgents,
    getAgentDetails,
    getUserAgents,
    buyAgent,
    listAgent,
    delistAgent,
    updateAgentPrice
  };
};