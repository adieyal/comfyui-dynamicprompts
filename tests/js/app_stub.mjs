// Stand-in for ComfyUI's scripts/app.js: records the registered extensions.
export const extensions = [];

export const app = {
  registerExtension(extension) {
    extensions.push(extension);
  },
};
