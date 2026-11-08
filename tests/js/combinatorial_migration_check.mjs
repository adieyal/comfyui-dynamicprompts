// Run by tests/test_combinatorial_migration.py as:
//   node --import ./tests/js/register.mjs tests/js/combinatorial_migration_check.mjs
// Exits non-zero, with a message on stderr, if any check fails.
import assert from "node:assert/strict";
import { extensions } from "./app_stub.mjs";

const { LAYOUT_KEY, LAYOUT_VERSION } = await import(
  new URL("../../web/js/combinatorial_migration.js", import.meta.url).href
);

assert.equal(extensions.length, 1, "the module registers one extension");
const [extension] = extensions;

// A fake node type whose configure/onNodeCreated record what they receive.
function makeNodeType() {
  const calls = { configure: [], onNodeCreated: 0 };
  function NodeType() {}
  NodeType.prototype.configure = function (info) {
    calls.configure.push(info);
  };
  NodeType.prototype.onNodeCreated = function () {
    calls.onNodeCreated += 1;
  };
  return { NodeType, calls };
}

function wrapped(name = "DPCombinatorialGenerator") {
  const { NodeType, calls } = makeNodeType();
  extension.beforeRegisterNodeDef(NodeType, { name });
  return { NodeType, calls, node: Object.assign(new NodeType(), { properties: {} }) };
}

const checks = {
  "4 values drop autorefresh, start at index 0 and gain the marker"() {
    const { node, calls } = wrapped();
    node.configure({ widgets_values: ["a {b|c}", 123, "fixed", "No"], properties: {} });
    const [info] = calls.configure;
    assert.deepEqual(info.widgets_values, ["a {b|c}", 0, "fixed"]);
    assert.equal(info.properties[LAYOUT_KEY], LAYOUT_VERSION);
  },

  "5 values keep save-to-metadata"() {
    const { node, calls } = wrapped();
    node.configure({
      widgets_values: ["a {b|c}", 123, "randomize", "No", "Yes"],
      properties: {},
    });
    const [info] = calls.configure;
    assert.deepEqual(info.widgets_values, ["a {b|c}", 0, "randomize", "Yes"]);
    assert.equal(info.properties[LAYOUT_KEY], LAYOUT_VERSION);
  },

  "info that already carries the marker passes through unchanged"() {
    const { node, calls } = wrapped();
    const info = {
      widgets_values: ["a {b|c}", 7, "fixed", "Yes"],
      properties: { [LAYOUT_KEY]: LAYOUT_VERSION },
    };
    node.configure(info);
    assert.equal(calls.configure[0], info);
    assert.deepEqual(calls.configure[0].widgets_values, ["a {b|c}", 7, "fixed", "Yes"]);
  },

  "the info passed in is not mutated"() {
    const { node } = wrapped();
    const info = {
      widgets_values: ["a {b|c}", 123, "fixed", "No"],
      properties: {},
    };
    node.configure(info);
    assert.deepEqual(info, {
      widgets_values: ["a {b|c}", 123, "fixed", "No"],
      properties: {},
    });
  },

  "onNodeCreated sets the layout marker"() {
    const { node, calls } = wrapped();
    node.onNodeCreated();
    assert.equal(calls.onNodeCreated, 1);
    assert.equal(node.properties[LAYOUT_KEY], LAYOUT_VERSION);
  },

  "a node type with another name is not wrapped"() {
    const { NodeType, calls } = makeNodeType();
    const { configure, onNodeCreated } = NodeType.prototype;
    extension.beforeRegisterNodeDef(NodeType, { name: "SomethingElse" });
    assert.equal(NodeType.prototype.configure, configure);
    assert.equal(NodeType.prototype.onNodeCreated, onNodeCreated);
    assert.equal(calls.configure.length, 0);
  },
};

const failures = [];
for (const [name, check] of Object.entries(checks)) {
  try {
    check();
  } catch (error) {
    failures.push(`FAIL: ${name}\n${error.message}`);
  }
}
if (failures.length > 0) {
  console.error(failures.join("\n\n"));
  process.exit(1);
}
