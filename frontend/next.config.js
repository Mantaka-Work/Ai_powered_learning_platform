/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    experimental: {
        serverActions: true,
    },
    images: {
        domains: ['localhost'],
    },
}

module.exports = nextConfig
