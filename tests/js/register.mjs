// Preloaded with `node --import`: lets web/js/combinatorial_migration.js load unchanged outside ComfyUI.
import { register } from "node:module";

register("./hooks.mjs", import.meta.url);
