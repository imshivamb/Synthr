import Image from "next/image";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { SiEthereum } from "react-icons/si";

interface AIAgent {
  id: string;
  name: string;
  description: string;
  image: string;
  price: string;
  creator: {
    address: string;
    name?: string;
  };
  category: string;
  capabilities: string[];
  tokenId: string;
}

interface AgentCardProps {
  agent: AIAgent;
}

export function AgentCard({ agent }: AgentCardProps) {
  return (
    <Card className="overflow-hidden transition-all hover:shadow-lg">
      <CardHeader className="p-0">
        <div className="relative aspect-square">
          <Image
            src={agent.image}
            alt={agent.name}
            fill
            className="object-cover"
          />
        </div>
      </CardHeader>
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-semibold truncate">{agent.name}</h3>
          <Badge variant="secondary">{agent.category}</Badge>
        </div>
        <p className="text-sm text-muted-foreground line-clamp-2 mb-4">
          {agent.description}
        </p>
        <div className="flex items-center text-sm text-muted-foreground">
          <span className="truncate">Created by </span>
          <span className="truncate font-medium ml-1">
            {agent.creator.name ||
              `${agent.creator.address.slice(
                0,
                6
              )}...${agent.creator.address.slice(-4)}`}
          </span>
        </div>
      </CardContent>
      <CardFooter className="p-4 pt-0 flex items-center justify-between">
        <div className="flex items-center">
          <SiEthereum className="h-4 w-4 mr-1" />
          <span className="font-semibold">{agent.price} ETH</span>
        </div>
        <Button>Buy Now</Button>
      </CardFooter>
    </Card>
  );
}
