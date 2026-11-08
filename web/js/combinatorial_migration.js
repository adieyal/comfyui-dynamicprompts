import { app } from "../../scripts/app.js";

// Layout 2 is [text, index, control, save_to_metadata]. Nodes of that layout carry this property in the
// workflow; a node without it was saved by 0.3.1 or earlier, where the values could not be told apart by shape.
export const LAYOUT_KEY = "dp_combinatorial_layout";
export const LAYOUT_VERSION = 2;

// Before layout 2 the node stored [text, seed, control, autorefresh] (0.2.0-0.3.0)
// or [text, seed, control, autorefresh, save_to_metadata] (0.3.1). Drop autorefresh, and start the node
// at index 0 instead of carrying the old seed over as the index; keep the control value.
// Any other shape (0.1.x stored only [text]) is left alone.
export function migrateOldLayout(values) {
  if (!Array.isArray(values)) return values;
  if (values.length === 4) return [values[0], 0, values[2]];
  if (values.length === 5) return [values[0], 0, values[2], values[4]];
  return values;
}

// Returns the node info to configure from, without changing the one passed in.
export function migrateInfo(info) {
  if (info.properties?.[LAYOUT_KEY] === LAYOUT_VERSION) return info;
  return {
    ...info,
    widgets_values: migrateOldLayout(info.widgets_values),
    properties: { ...info.properties, [LAYOUT_KEY]: LAYOUT_VERSION },
  };
}

app.registerExtension({
  name: "dynamicprompts.CombinatorialMigration",
  beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData.name !== "DPCombinatorialGenerator") return;

    const onNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function (...args) {
      const result = onNodeCreated?.apply(this, args);
      this.properties[LAYOUT_KEY] = LAYOUT_VERSION;
      return result;
    };

    const configure = nodeType.prototype.configure;
    nodeType.prototype.configure = function (info) {
      return configure.call(this, migrateInfo(info));
    };
  },
});
