export default {
  distDir: process.env.MELKA_NEXT_DIST_DIR || '.next',
  trailingSlash: true,
  poweredByHeader: false,
  // Use TypeScript's compiler API. This avoids Next invoking TypeScript's
  // extensionless CLI wrapper, which Node 24 treats as an empty script.
  experimental: { useTypeScriptCli: false },
};
