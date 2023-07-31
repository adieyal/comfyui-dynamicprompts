from dynamicprompts.generators import FeelingLuckyGenerator, RandomPromptGenerator

from .generator import DPGeneratorNode


class DPFeelingLucky(DPGeneratorNode):
    def generate_prompt(self, text) -> str:
        prompt_generator = FeelingLuckyGenerator(generator=RandomPromptGenerator())

        all_prompts = prompt_generator.generate(text, 1) or [""]
        return all_prompts[0]
