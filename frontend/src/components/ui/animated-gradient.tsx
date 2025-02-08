"use client";

import { motion } from "framer-motion";

export function AnimatedGradient() {
  return (
    <motion.div
      className="absolute inset-0 -z-10"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:50px_50px]" />
      <div className="absolute left-0 right-0 top-0 -z-10 m-auto h-[300px] w-[300px] rounded-full bg-gradient-to-r from-purple-600 to-blue-600 opacity-20 blur-[100px]" />
      <div className="absolute right-0 top-0 -z-10 h-[300px] w-[300px] rounded-full bg-gradient-to-r from-blue-600 to-purple-600 opacity-20 blur-[100px]" />
    </motion.div>
  );
}
