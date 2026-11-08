# ComfyUI-DynamicPrompts Custom Nodes

<img src="images/example.png"/>

ComfyUI-DynamicPrompts is a custom nodes library that integrates into your existing ComfyUI Library. It provides nodes that enable the use of [Dynamic Prompts](https://github.com/adieyal/dynamicprompts) in your ComfyUI. The nodes provided in this library are:

1. Random Prompts - Randomly samples variants and wildcards.
2. Combinatorial Prompts - Walks through every possible combination of the variants and wildcards in a prompt.
3. Magic Prompt - Employs a neural network to add relevant modifiers to your prompt. The model is loaded on first use, so ComfyUI starts quickly. It needs `transformers`, which is not installed automatically so that your existing version is left alone; most ComfyUI installs already have it.
4. Jinja2 Templates - Allows you to write prompts using Jinja2 templates. Templates can call `wildcard("...")` and import other templates from the wildcard folder.
5. OutputString - Deprecated and hidden from the node menu; it is kept so old workflows still load. To see a generated prompt, connect it to ComfyUI's Preview Any node.

The prompt syntax (variants, wildcards, weights and more) is described in the [Dynamic Prompts syntax docs](https://github.com/adieyal/dynamicprompts/blob/main/docs/SYNTAX.md).

Nodes can be found in the Dynamic Prompts menu:
<img src="images/menu.png"/>

## Useful Links
* [Dynamic Prompts Home](https://github.com/adieyal/dynamicprompts)
* [Dynamic Prompts Syntax](https://github.com/adieyal/dynamicprompts/blob/main/docs/SYNTAX.md)
* [Dynamic Prompts Extension for Auto1111](https://github.com/adieyal/sd-dynamic-prompts)
* [Tutorial](https://github.com/adieyal/sd-dynamic-prompts/blob/main/docs/tutorial.md)
* [Online Resources](https://github.com/adieyal/sd-dynamic-prompts/blob/main/docs/resources.md)
* [CHANGELOG](./docs/CHANGELOG.md)
* [Stable Diffusion SDXL Wildcards and ComfyUI](https://ericri.medium.com/stable-diffusion-sdxl-wildcards-and-comfyui-e8483e00e1c)

## Installation

### Using ComfyUI-Manager
1. Install [ComfyUI-Manager](https://github.com/ltdrdata/ComfyUI-Manager) if it isn't already.
2. Press Install Custom Nodes from the ComfyUI-Manager menu
3. Search for dynamicprompts
4. Click install

### Manual installation

Follow the steps below to install the ComfyUI-DynamicPrompts Library. These commands assume the your current working directory is the ComfyUI root directory.

1. Clone the repository:
   ```
   git clone https://github.com/adieyal/comfyui-dynamicprompts custom_nodes/comfyui-dynamicprompts
   ```
2. Install the required Python packages:
   ```
   python -m pip install -r custom_nodes/comfyui-dynamicprompts/requirements.txt
   ```
3. (Optional) download a wildcard collection and copy it into `ComfyUI/wildcards` (see Wildcards below).
4. Restart your ComfyUI.
5. Example workflows can be found in `custom_nodes/comfyui-dynamicprompts/example_workflows`.

## Wildcards
Put wildcard files in `ComfyUI/wildcards` or in this extension's `wildcards` folder (`custom_nodes/comfyui-dynamicprompts/wildcards`). Extra folders can be added under a `wildcards` key in ComfyUI's `extra_model_paths.yaml`. Wildcard files can be `.txt`, `.json` or `.yaml` ([example format](https://github.com/adieyal/sd-dynamic-prompts/blob/main/collections/publicprompts.yaml)). Edits are picked up on the next run, so you don't need to restart ComfyUI.

There are many pre-built wildcards collections available. Here are a few to get you started:
* [SD Dynamic Prompts built-in](https://github.com/adieyal/sd-dynamic-prompts/tree/main/collections)
* [Civitai wildcard packs](https://github.com/adieyal/sd-dynamic-prompts/blob/main/docs/resources.md#wildcard-packs)


## Node Outputs

All nodes in this library produce a String output that can typically be passed into Clip Text Encode Prompts. Both positive and negative nodes are supported.

Seeds and refreshing:

- **Random Prompts**: the same text, seed and wildcard files give the same prompt. The seed widget has "control after generate" (fixed, increment, decrement or randomize). Setting `autorefresh` to Yes gives a new random prompt on every run, whatever the seed.
- **Combinatorial Prompts**: the seed is the index of the combination to output, and it wraps around. A second output gives the total number of combinations, so setting the seed to increment walks through all of them. For example, A `{red|green|blue}` ball gives A red ball, A green ball, A blue ball, then A red ball again. Setting `autorefresh` to Yes picks a random combination on every run.
- **Magic Prompt** works like Random Prompts: the same text and seed give the same prompt, and `autorefresh` set to Yes gives a new prompt on every run.
- **Jinja2 Templates** has no seed. With `autorefresh` set to No, the result is reused until the template or the wildcard files change; with Yes, the template is rendered again on every run.

### Saving the prompt in the image

ComfyUI's image metadata stores the template (`a {red|blue} ball`), not the prompt the node generated. Set `save_to_metadata` to Yes on a node to also store the generated prompt: images saved by Save Image get a `dynamicprompts` entry such as `{"5": "a blue ball"}`, keyed by node id. A cached node can't write metadata, so with this option on the node runs on every queue.
