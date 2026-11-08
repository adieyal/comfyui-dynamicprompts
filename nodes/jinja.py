from __future__ import annotations

import logging
from typing import Any

from dynamicprompts.generators import JinjaGenerator

from .sampler import METADATA_INPUTS, Autorefresh, SaveToMetadata, save_prompt
from .wildcards import change_key, get_wildcard_manager

logger = logging.getLogger(__name__)


class DPJinja:
    RETURN_TYPES = ("STRING",)
    FUNCTION = "get_prompt"
    CATEGORY = "Dynamic Prompts"

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, dict[str, Any]]:
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "dynamicPrompts": False}),
                "autorefresh": (["Yes", "No"],),
            },
            **METADATA_INPUTS,
        }

    @classmethod
    def IS_CHANGED(
        cls,
        text: str,
        autorefresh: Autorefresh,
        save_to_metadata: SaveToMetadata = "No",
        extra_pnginfo: dict[str, Any] | None = None,
        unique_id: str | None = None,
    ) -> float | str:
        # A cached node doesn't run, so it couldn't write this run's metadata.
        if autorefresh == "Yes" or save_to_metadata == "Yes":
            return float("nan")
        return change_key(text)

    def get_prompt(
        self,
        text: str,
        autorefresh: Autorefresh,
        save_to_metadata: SaveToMetadata = "No",
        extra_pnginfo: dict[str, Any] | None = None,
        unique_id: str | None = None,
    ) -> tuple[str]:
        generator = JinjaGenerator(get_wildcard_manager())
        prompt = str(generator.generate(text, 1)[0])
        logger.info("Jinja prompt: %s", prompt)
        if save_to_metadata == "Yes":
            save_prompt(extra_pnginfo, unique_id, prompt)
        return (prompt,)
