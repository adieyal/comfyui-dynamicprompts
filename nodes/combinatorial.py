from __future__ import annotations

import logging
import random

from dynamicprompts.generators import CombinatorialPromptGenerator

from .sampler import Autorefresh, DPSeededNode
from .wildcards import get_wildcard_manager

logger = logging.getLogger(__name__)

# Enumeration stops here so templates with huge (or endless) combinations stay usable.
MAX_COMBINATIONS = 10_000


class DPCombinatorialGenerator(DPSeededNode):
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("prompt", "combinations")

    def get_prompt(
        self,
        text: str,
        seed: int,
        autorefresh: Autorefresh,
    ) -> tuple[str, int]:
        generator = CombinatorialPromptGenerator(get_wildcard_manager())
        prompts = generator.generate(text, max_prompts=MAX_COMBINATIONS)
        count = len(prompts)
        if count >= MAX_COMBINATIONS:
            logger.warning(
                "Template has at least %d combinations; only the first %d are used.",
                MAX_COMBINATIONS,
                MAX_COMBINATIONS,
            )
        if count == 0:
            logger.warning("Template produced no combinations: %r", text)
            return ("", 0)

        index = random.randrange(count) if autorefresh == "Yes" else seed % count
        prompt = prompts[index]
        logger.info("Combinatorial prompt %d of %d: %s", index + 1, count, prompt)
        return (prompt, count)
