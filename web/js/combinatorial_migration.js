import { app } from "../../scripts/app.js";

// Workflows saved with 0.3.x stored [text, seed, control, autorefresh, save_to_metadata].
// The node now has [text, index, control, save_to_metadata]: drop autorefresh so the rest line up.
export function dropAutorefresh(values) {
  if (!Array.isArray(values) || values.length !== 5) return values;
  return [values[0], values[1], values[2], values[4]];
}

app.registerExtension({
  name: "dynamicprompts.CombinatorialMigration",
  beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData.name !== "DPCombinatorialGenerator") return;
    const configure = nodeType.prototype.configure;
    nodeType.prototype.configure = function (info) {
      info.widgets_values = dropAutorefresh(info.widgets_values);
      return configure.call(this, info);
    };
  },
});
