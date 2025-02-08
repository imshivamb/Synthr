export interface AIAgent {
    id: string;
    tokenId: string;
    name: string;
    description: string;
    image: string;
    price: string;
    creator: {
      address: string;
      name?: string;
    };
    category: AgentCategory;
    capabilities: string[];
    metadata: AgentMetadata;
  }
  
  export interface AgentMetadata {
    modelType: string;
    version: string;
    created: string;
    updated: string;
    stats: {
      uses: number;
      ratings: number;
      averageRating: number;
    };
  }
  
  export type AgentCategory = 
    | 'Analytics'
    | 'Content Generation'
    | 'Data Processing'
    | 'Automation'
    | 'Trading'
    | 'Creative'
    | 'All';
  
  export type SortOption = 
    | 'latest'
    | 'price-low'
    | 'price-high'
    | 'popular';
  
  export interface MarketplaceFilters {
    search: string;
    category: AgentCategory;
    sortBy: SortOption;
    priceRange: {
      min: number;
      max: number;
    };
    page: number;
  }