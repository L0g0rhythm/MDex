/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export', // Required for Tauri static hosting
  images: {
    unoptimized: true, // Required for static export
  },
};

export default nextConfig;
