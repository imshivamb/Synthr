"use client";

import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import Link from "next/link";

import { AnimatedGradient } from "@/components/ui/animated-gradient";

export default function Home() {
  return (
    <div className="flex flex-col min-h-[calc(100vh-4rem)] relative overflow-hidden">
      <AnimatedGradient />
      {/* Hero Section */}
      <section className="flex-1 flex flex-col items-center justify-center space-y-10 px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center space-y-4"
        >
          <motion.h1
            className="text-6xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-blue-600"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            SYNTHR
          </motion.h1>
          <motion.p
            className="text-2xl text-muted-foreground"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            The Future of AI Agent Trading
          </motion.p>
        </motion.div>

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
