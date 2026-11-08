from __future__ import annotations

import logging
import random

from dynamicprompts.generators import CombinatorialPromptGenerator
from dynamicprompts.samplers.count import UnboundedCount

from .sampler import Autorefresh, DPSeededNode
from .wildcards import get_wildcard_manager

logger = logging.getLogger(__name__)


class DPCombinatorialGenerator(DPSeededNode):
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("prompt", "combinations")

    def get_prompt(
        self,
        text: str,
        seed: int,
        autorefresh: Autorefresh,
    ) -> tuple[str, int]:
        # The seed also fixes random choices inside the template ({~a|b}), so an index always gives the same prompt.
        generator = CombinatorialPromptGenerator(
            get_wildcard_manager(),
            seed=None if autorefresh == "Yes" else seed,
        )
        result = generator.count(text)
        if isinstance(result, UnboundedCount):
            raise ValueError(
                "Template contains a recursive wildcard, so its number of combinations is unbounded.",
            )
        count = result.value
        if count == 0:
            logger.warning("Template produced no combinations: %r", text)
            return ("", 0)
        if result.has_random_parts:
            logger.debug("Template has random parts; the seed fixes their choices.")

        index = random.randrange(count) if autorefresh == "Yes" else seed % count
        prompt = generator.prompt_at(text, index)
        logger.info("Combinatorial prompt %d of %d: %s", index + 1, count, prompt)
        return (prompt, count)
