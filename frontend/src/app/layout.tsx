import type { Metadata } from "next";
import { Inter, JetBrains_Mono, Space_Grotesk } from "next/font/google";
import "./globals.css";
import Providers from "@/providers";

// Primary font for body text
const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600"],
});

// Font for headings
const space = Space_Grotesk({
  variable: "--font-space",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

// Font for code, blockchain addresses, and AI-related text
const mono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
  weight: ["400", "500"],
});

export const metadata: Metadata = {
  title: "AI Agent Marketplace",
  description: "Buy, sell, and create AI assistants powered by Web3",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body
        className={`${inter.className} ${space.variable} ${mono.variable} antialiased`}
      >
        <Providers>
          <div className="min-h-screen">
            <main className="">{children}</main>
          </div>
        </Providers>
      </body>
    </html>
  );
}
