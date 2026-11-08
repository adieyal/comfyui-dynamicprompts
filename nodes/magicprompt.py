from __future__ import annotations

import logging

from dynamicprompts.generators import RandomPromptGenerator

from .sampler import Autorefresh, DPSeededNode
from .wildcards import get_wildcard_manager

logger = logging.getLogger(__name__)

# transformers.set_seed seeds numpy, which only accepts 32-bit seeds.
_SEED_MODULUS = 2**32


class DPMagicPrompt(DPSeededNode):
    def get_prompt(self, text: str, seed: int, autorefresh: Autorefresh) -> tuple[str]:
        run_seed = None if autorefresh == "Yes" else seed % _SEED_MODULUS
        # Imported here so that loading the package never imports transformers.
        # The library keeps the loaded pipeline on the class, so the model loads once.
        # Errors propagate so ComfyUI fails the run and shows them.
        from dynamicprompts.generators.magicprompt import MagicPromptGenerator

        generator = MagicPromptGenerator(
            prompt_generator=RandomPromptGenerator(
                get_wildcard_manager(),
                seed=run_seed,
            ),
            seed=run_seed,
        )
        prompts = generator.generate(text, 1)
        if not prompts:
            logger.warning("Template produced no prompt: %r", text)
            return ("",)
        prompt = str(prompts[0])
        logger.info("Magic prompt: %s", prompt)
        return (prompt,)
