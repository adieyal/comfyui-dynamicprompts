from __future__ import annotations

import logging
from typing import Any

from dynamicprompts.generators import CombinatorialPromptGenerator
from dynamicprompts.samplers.count import UnboundedCount

from .sampler import METADATA_INPUTS, SaveToMetadata, save_prompt
from .wildcards import change_key, get_wildcard_manager, may_use_wildcards

logger = logging.getLogger(__name__)


class DPCombinatorialGenerator:
    """Outputs combination `index % count` of the template, and the count.

    Takes an `index` instead of the seed and autorefresh inputs of DPSeededNode.
    """

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("prompt", "combinations")
    FUNCTION = "run"
    CATEGORY = "Dynamic Prompts"

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, dict[str, Any]]:
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "dynamicPrompts": False}),
                "index": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 0xFFFFFFFFFFFFFFFF,
                        "control_after_generate": "increment",
                    },
                ),
            },
            **METADATA_INPUTS,
        }

    @classmethod
    def IS_CHANGED(
        cls,
        text: str,
        index: int,
        save_to_metadata: SaveToMetadata = "No",
        extra_pnginfo: dict[str, Any] | None = None,
        unique_id: str | None = None,
    ) -> float | str:
        # A cached node doesn't run, so it couldn't write this run's metadata.
        if save_to_metadata == "Yes":
            return float("nan")
        return change_key(text, index, scan_wildcards=may_use_wildcards(text))

    def run(
        self,
        text: str,
        index: int,
        save_to_metadata: SaveToMetadata = "No",
        extra_pnginfo: dict[str, Any] | None = None,
        unique_id: str | None = None,
    ) -> tuple[str, int]:
        result = self.get_prompt(text, index)
        if save_to_metadata == "Yes":
            save_prompt(extra_pnginfo, unique_id, result[0])
        return result

    def get_prompt(self, text: str, index: int) -> tuple[str, int]:
        # Seeding with the index fixes random choices inside the template ({~a|b}): an index always gives
        # the same prompt, and index + count gives the same combination with fresh random choices.
        generator = CombinatorialPromptGenerator(
            get_wildcard_manager(may_use_wildcards(text)),
            seed=index,
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
            logger.debug("Template has random parts; the index fixes their choices.")

        position = index % count
        prompt = generator.prompt_at(text, position)
        logger.info("Combinatorial prompt %d of %d: %s", position + 1, count, prompt)
        return (prompt, count)
