"use client";

import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { Spotlight } from "@/components/ui/spotlight";
import { Navbar } from "@/components/layout/navbar";

export default function Home() {
  return (
    <div className="flex flex-col min-h-[calc(100vh-4rem)] relative overflow-hidden">
      <Navbar />
      {/* Hero Section */}
      <section className="flex-1 flex flex-col items-center justify-center space-y-10">
        <div className="h-[40rem] w-full flex md:items-center md:justify-center bg-black/[0.96] antialiased bg-grid-white/[0.02] relative overflow-hidden">
          <Spotlight />
          <div className=" p-4 max-w-7xl  mx-auto relative z-10  w-full pt-20 md:pt-0">
            <h1 className="text-4xl mx-auto max-w-4xl md:text-7xl font-bold text-center bg-clip-text text-transparent bg-gradient-to-b from-neutral-50 to-neutral-400 bg-opacity-50">
              The Future of AI Agent Trading
            </h1>
            <p className=" mt-8 text-lg font-normal text-neutral-300 max-w-lg text-center mx-auto">
              Transform the way you interact with AI. Create, trade, and own
              powerful AI agents in a decentralized marketplace.
            </p>
          </div>
        </div>

        {/* Animated Stats Section */}
        <motion.div
          className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full max-w-3xl"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
        >
          <div className="text-center">
            <h3 className="text-3xl font-bold">100+</h3>
            <p className="text-muted-foreground">AI Agents</p>
          </div>
          <div className="text-center">
            <h3 className="text-3xl font-bold">50k+</h3>
            <p className="text-muted-foreground">Users</p>
          </div>
          <div className="text-center">
            <h3 className="text-3xl font-bold">$2M+</h3>
            <p className="text-muted-foreground">Trading Volume</p>
          </div>
        </motion.div>

        {/* CTA Buttons */}
        <motion.div
          className="flex gap-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.8 }}
        >
          <Link href="/marketplace">
            <Button
              size="lg"
              className="bg-gradient-to-r from-purple-600 to-blue-600 text-white"
            >
              Explore Marketplace
            </Button>
          </Link>
          <Link href="/create">
            <Button size="lg" variant="outline">
              Create Agent
            </Button>
          </Link>
        </motion.div>
      </section>

      {/* Animated Feature Cards */}
      <motion.section
        className="grid grid-cols-1 md:grid-cols-3 gap-6 px-4 py-16 bg-muted/50"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8, delay: 1 }}
      >
        <motion.div
          className="p-6 bg-background rounded-lg shadow-lg"
          whileHover={{ scale: 1.05 }}
          transition={{ type: "spring", stiffness: 300 }}
        >
          <h3 className="text-xl font-bold mb-2">Create</h3>
          <p className="text-muted-foreground">
            Build and customize your own AI agents with ease
          </p>
        </motion.div>
        <motion.div
          className="p-6 bg-background rounded-lg shadow-lg"
          whileHover={{ scale: 1.05 }}
          transition={{ type: "spring", stiffness: 300 }}
        >
          <h3 className="text-xl font-bold mb-2">Trade</h3>
          <p className="text-muted-foreground">
            Buy and sell AI agents in a secure marketplace
          </p>
        </motion.div>
        <motion.div
          className="p-6 bg-background rounded-lg shadow-lg"
          whileHover={{ scale: 1.05 }}
          transition={{ type: "spring", stiffness: 300 }}
        >
          <h3 className="text-xl font-bold mb-2">Earn</h3>
          <p className="text-muted-foreground">
            Generate revenue from your AI creations
          </p>
        </motion.div>
      </motion.section>
    </div>
  );
}
