// Module-resolution hooks: point ComfyUI's app.js import at a stub, and load the extension as an ES module
// (web/ has no package.json, so Node would otherwise treat the .js file as CommonJS).
const STUB_URL = new URL("./app_stub.mjs", import.meta.url).href;

export async function resolve(specifier, context, nextResolve) {
  if (specifier === "../../scripts/app.js") {
    return { url: STUB_URL, shortCircuit: true };
  }
  return nextResolve(specifier, context);
}

export async function load(url, context, nextLoad) {
  if (url.endsWith("/web/js/combinatorial_migration.js")) {
    return nextLoad(url, { ...context, format: "module" });
  }
  return nextLoad(url, context);
}
