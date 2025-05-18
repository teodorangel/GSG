import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/admin/:path*',
        destination: 'http://localhost:8000/api/admin/:path*',
      },
    ];
  },
};

export default nextConfig;
