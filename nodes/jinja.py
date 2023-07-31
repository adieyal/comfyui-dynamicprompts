from dynamicprompts.generators import JinjaGenerator

from .generator import DPGeneratorNode


class DPJinja(DPGeneratorNode):
    def generate_prompt(self, text):
        prompt_generator = JinjaGenerator()

        all_prompts = prompt_generator.generate(text, 1) or [""]
        return all_prompts[0]
