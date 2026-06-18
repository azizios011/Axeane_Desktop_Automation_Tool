import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Required for Tauri to serve the app from a folder
  output: 'export',

  // Required because Tauri doesn't have a Node.js server to optimize images
  images: {
    unoptimized: true,
  },

  // Optional: Prevents potential issues with double-rendering in Dev
  reactStrictMode: true,

  reactCompiler: true,
};

export default nextConfig;
