/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Remove output: 'export' - this app requires client-side JavaScript
  // For Vercel/Netlify/AWS Amplify: no output config needed (default)
  // For standalone server: use output: 'standalone'
  // For static export: NOT RECOMMENDED for this app (requires authentication)
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
}

module.exports = nextConfig

