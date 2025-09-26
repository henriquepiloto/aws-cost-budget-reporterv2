/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  experimental: {
    outputFileTracingRoot: undefined,
  },
  env: {
    API_URL: process.env.API_URL || 'https://costs.selectsolucoes.com',
    DB_HOST: process.env.DB_HOST || 'glpi-database-instance-1.cnhjpcs7r4ar.us-east-1.rds.amazonaws.com',
  }
}

module.exports = nextConfig
