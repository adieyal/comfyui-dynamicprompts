from __future__ import annotations

import logging
from typing import Any

from dynamicprompts.generators import JinjaGenerator

from .sampler import Autorefresh
from .wildcards import change_key, get_wildcard_manager

logger = logging.getLogger(__name__)


class DPJinja:
    RETURN_TYPES = ("STRING",)
    FUNCTION = "get_prompt"
    CATEGORY = "Dynamic Prompts"

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, dict[str, tuple[Any, ...]]]:
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "dynamicPrompts": False}),
                "autorefresh": (["Yes", "No"],),
            },
        }

    @classmethod
    def IS_CHANGED(cls, text: str, autorefresh: Autorefresh) -> float | str:
        if autorefresh == "Yes":
            return float("nan")
        return change_key(text)

    def get_prompt(self, text: str, autorefresh: Autorefresh) -> tuple[str]:
        generator = JinjaGenerator(get_wildcard_manager())
        prompt = str(generator.generate(text, 1)[0])
        logger.info("Jinja prompt: %s", prompt)
        return (prompt,)
