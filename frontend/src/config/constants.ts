export const CATEGORIES = [
    'All',
    'Analytics',
    'Content Generation',
    'Data Processing',
    'Automation',
    'Trading',
    'Creative',
  ] as const;
  
  export const SORT_OPTIONS = [
    { label: 'Latest', value: 'latest' },
    { label: 'Price: Low to High', value: 'price-low' },
    { label: 'Price: High to Low', value: 'price-high' },
    { label: 'Most Popular', value: 'popular' },
  ] as const;
  
  export const PRICE_RANGE = {
    MIN: 0,
    MAX: 10,
    STEP: 0.1,
  } as const;