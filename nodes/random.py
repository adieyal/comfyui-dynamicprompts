from __future__ import annotations

import logging

from dynamicprompts.generators import RandomPromptGenerator

from .sampler import Autorefresh, DPSeededNode
from .wildcards import get_wildcard_manager, may_use_wildcards

logger = logging.getLogger(__name__)


class DPRandomGenerator(DPSeededNode):
    def get_prompt(self, text: str, seed: int, autorefresh: Autorefresh) -> tuple[str]:
        generator = RandomPromptGenerator(
            get_wildcard_manager(may_use_wildcards(text)),
            seed=None if autorefresh == "Yes" else seed,
        )
        prompts = generator.generate(text, 1)
        if not prompts:
            logger.warning("Template produced no prompt: %r", text)
            return ("",)
        prompt = str(prompts[0])
        logger.info("Random prompt: %s", prompt)
        return (prompt,)
