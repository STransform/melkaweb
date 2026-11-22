import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);

export default {
  distDir: process.env.MELKA_NEXT_DIST_DIR || '.next',
  trailingSlash: true,
  poweredByHeader: false,
  allowedDevOrigins: ['localhost', '127.0.0.1'],
  // Use TypeScript's compiler API. This avoids Next invoking TypeScript's
  // extensionless CLI wrapper, which Node 24 treats as an empty script.
  experimental: {
    useTypeScriptCli: false,
    ...(process.env.MELKA_LOW_MEMORY_BUILD === '1' ? {
      cpus: 1,
      webpackBuildWorker: true,
      webpackMemoryOptimizations: true,
    } : {}),
  },
  // Only set this after a separate successful `npm run typecheck`.
  typescript: {
    ignoreBuildErrors: process.env.MELKA_TYPES_PRECHECKED === '1',
  },
  // Older cPanel hosts cannot load native SWC; its WASM minifier can crash.
  // Opt into Terser for those hosts while retaining production minification.
  webpack(config, { dev }) {
    if (!dev && process.env.MELKA_USE_TERSER === '1') {
      const TerserPlugin = require('terser-webpack-plugin');
      // Next's first minimizer is a function that applies its SWC plugin.
      // Keep the remaining minimizers, including CSS optimization.
      config.optimization.minimizer = [
        new TerserPlugin({ parallel: false }),
        ...config.optimization.minimizer.slice(1),
      ];
    }
    return config;
  },
};
