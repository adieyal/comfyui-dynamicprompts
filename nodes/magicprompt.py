from dynamicprompts.generators import RandomPromptGenerator
from dynamicprompts.generators.magicprompt import MagicPromptGenerator

from .generator import DPGeneratorNode


class DPMagicPrompt(DPGeneratorNode):
    def generate_prompt(self, text, seed):
        prompt_generator = MagicPromptGenerator(
            prompt_generator=RandomPromptGenerator(seed=seed),
        )

        all_prompts = prompt_generator.generate(text, 1) or [""]
        return all_prompts[0]
