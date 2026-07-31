import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.API_BACKEND_URL || "http://localhost:8000"}/api/:path*`,
      },
      {
        source: "/health",
        destination: `${process.env.API_BACKEND_URL || "http://localhost:8000"}/health`,
      },
      {
        source: "/ready",
        destination: `${process.env.API_BACKEND_URL || "http://localhost:8000"}/ready`,
      },
      {
        source: "/openapi.json",
        destination: `${process.env.API_BACKEND_URL || "http://localhost:8000"}/openapi.json`,
      },
    ];
  },
};

export default nextConfig;