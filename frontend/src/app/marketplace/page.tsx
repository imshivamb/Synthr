"use client";

import { useEffect } from "react";
import { useMarketplaceStore } from "@/store/useMarketplaceStore";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { AgentCard } from "@/components/marketplace/agent-card";
import { useMarketplaceService } from "@/hooks/useMarketplaceService";
import { CATEGORIES } from "@/config/constants";
import { AgentCategory, MarketplaceFilters } from "@/types/marketplace";

export default function MarketplacePage() {
  const {
    agents,
    isLoading,
    error,
    filters,
    setAgents,
    setLoading,
    setError,
    setFilter,
    resetFilters,
  } = useMarketplaceStore();

  const marketplaceService = useMarketplaceService();

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        setLoading(true);
        const fetchedAgents = await marketplaceService.getAgents(filters);
        setAgents(fetchedAgents);
      } catch (err) {
        console.error("Error fetching agents:", err);
        setError("Failed to fetch agents");
      } finally {
        setLoading(false);
      }
    };

    fetchAgents();
  }, [filters, marketplaceService]);

  return (
    <div className="min-h-screen">
      {/* Header */}
      <div className="border-b">
        <div className="container py-6">
          <h1 className="text-3xl font-bold">Marketplace</h1>
          <p className="text-muted-foreground mt-2">
            Discover and collect powerful AI agents
          </p>
        </div>
      </div>

      <div className="container py-6">
        <div className="grid grid-cols-12 gap-6">
          {/* Filters Sidebar */}
          <div className="col-span-3 space-y-6">
            <Card className="p-4">
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold mb-2">Search</h3>
                  <Input
                    placeholder="Search agents..."
                    value={filters.search}
                    onChange={(e) => setFilter("search", e.target.value)}
                  />
                </div>

                <div>
                  <h3 className="font-semibold mb-2">Category</h3>
                  <Select
                    value={filters.category}
                    onValueChange={(value: AgentCategory) =>
                      setFilter("category", value)
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select category" />
                    </SelectTrigger>
                    <SelectContent>
                      {CATEGORIES.map((category) => (
                        <SelectItem key={category} value={category}>
                          {category}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <h3 className="font-semibold mb-2">Price Range</h3>
                  <div className="pt-2">
                    <div className="mb-4">
                      <div className="flex justify-between text-sm text-muted-foreground">
                        <span>{filters.priceRange.min} ETH</span>
                        <span>{filters.priceRange.max} ETH</span>
                      </div>
                      <Slider
                        defaultValue={[
                          filters.priceRange.min,
                          filters.priceRange.max,
                        ]}
                        min={0}
                        max={10}
                        step={0.1}
                        onValueChange={(values: number[]) =>
                          setFilter("priceRange", {
                            min: values[0],
                            max: values[1],
                          })
                        }
                      />
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold mb-2">Sort By</h3>
                  <Select
                    value={filters.sortBy}
                    onValueChange={(value: MarketplaceFilters["sortBy"]) =>
                      setFilter("sortBy", value)
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Sort by" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="latest">Latest</SelectItem>
                      <SelectItem value="price-low">
                        Price: Low to High
                      </SelectItem>
                      <SelectItem value="price-high">
                        Price: High to Low
                      </SelectItem>
                      <SelectItem value="popular">Most Popular</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <Button
                  variant="outline"
                  className="w-full"
                  onClick={resetFilters}
                >
                  Reset Filters
                </Button>
              </div>
            </Card>
          </div>

          {/* Agents Grid */}
          <div className="col-span-9">
            {isLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[...Array(6)].map((_, i) => (
                  <Card key={i} className="h-[400px] animate-pulse" />
                ))}
              </div>
            ) : error ? (
              <div className="text-center text-red-500">{error}</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {agents.map((agent) => (
                  <AgentCard key={agent.id} agent={agent} />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
