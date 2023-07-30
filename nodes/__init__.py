from comfy_dynamicprompts.nodes.combinatorial import DPCombinatorialGenerator
from comfy_dynamicprompts.nodes.feeling_lucky import DPFeelingLucky
from comfy_dynamicprompts.nodes.jinja import DPJinja
from comfy_dynamicprompts.nodes.magicprompt import DPMagicPrompt
from comfy_dynamicprompts.nodes.random import DPRandomGenerator

NODE_CLASS_MAPPINGS = {
    "DPRandomGenerator": DPRandomGenerator,
    "DPCombinatorialGenerator": DPCombinatorialGenerator,
    "DPFeelingLucky": DPFeelingLucky,
    "DPJinja": DPJinja,
    "DPMagicPrompt": DPMagicPrompt,
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "DPRandomGenerator": "Random Prompts",
    "DPCombinatorialGenerator": "Combinatorial Prompts",
    "DPFeelingLucky": "I'm Feeling Lucky",
    "DPJinja": "Jinja2 Templates",
    "DPMagicPrompt": "Magic Prompt",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
