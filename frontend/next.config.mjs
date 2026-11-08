export default {
  trailingSlash: true,
  poweredByHeader: false,
  // Use TypeScript's compiler API. This avoids Next invoking TypeScript's
  // extensionless CLI wrapper, which Node 24 treats as an empty script.
  experimental: { useTypeScriptCli: false },
};
