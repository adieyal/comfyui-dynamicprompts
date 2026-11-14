from __future__ import annotations

import logging
from typing import Any, Literal

from .wildcards import change_key, may_use_wildcards

logger = logging.getLogger(__name__)

Autorefresh = Literal["Yes", "No"]
SaveToMetadata = Literal["Yes", "No"]

# Key under which generated prompts are written to the image metadata, as {node id: prompt}.
METADATA_KEY = "dynamicprompts"

# Shared by every generator node. `save_to_metadata` is optional so saved workflows keep their widget order.
METADATA_INPUTS: dict[str, dict[str, Any]] = {
    "optional": {
        "save_to_metadata": (
            ["No", "Yes"],
            {
                "default": "No",
                "tooltip": "Write the generated prompt into the saved image's metadata. "
                "The node then runs on every queue instead of being cached.",
            },
        ),
    },
    "hidden": {"extra_pnginfo": "EXTRA_PNGINFO", "unique_id": "UNIQUE_ID"},
}


def save_prompt(
    extra_pnginfo: dict[str, Any] | None,
    unique_id: str | None,
    prompt: str,
) -> None:
    """Add the prompt to the metadata that ComfyUI's save nodes write into the image."""
    if extra_pnginfo is None or unique_id is None:
        logger.warning(
            "save_to_metadata is on, but this run has no image metadata to write to "
            "(queued without extra_pnginfo).",
        )
        return
    extra_pnginfo.setdefault(METADATA_KEY, {})[unique_id] = prompt


class DPSeededNode:
    """Inputs and caching shared by the Random and MagicPrompt nodes."""

    RETURN_TYPES: tuple[str, ...] = ("STRING",)
    FUNCTION = "run"
    CATEGORY = "Dynamic Prompts"

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, dict[str, Any]]:
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "dynamicPrompts": False}),
                "seed": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 0xFFFFFFFFFFFFFFFF,
                        "control_after_generate": True,
                    },
                ),
                "autorefresh": (["Yes", "No"], {"default": "No"}),
            },
            **METADATA_INPUTS,
        }

    @classmethod
    def IS_CHANGED(
        cls,
        text: str,
        seed: int,
        autorefresh: Autorefresh,
        save_to_metadata: SaveToMetadata = "No",
        extra_pnginfo: dict[str, Any] | None = None,
        unique_id: str | None = None,
    ) -> float | str:
        # A cached node doesn't run, so it couldn't write this run's metadata.
        if autorefresh == "Yes" or save_to_metadata == "Yes":
            return float("nan")
        return change_key(text, seed, scan_wildcards=may_use_wildcards(text))

    def run(
        self,
        text: str,
        seed: int,
        autorefresh: Autorefresh,
        save_to_metadata: SaveToMetadata = "No",
        extra_pnginfo: dict[str, Any] | None = None,
        unique_id: str | None = None,
    ) -> tuple[Any, ...]:
        result = self.get_prompt(text, seed, autorefresh)
        if save_to_metadata == "Yes":
            save_prompt(extra_pnginfo, unique_id, result[0])
        return result

    def get_prompt(
        self, text: str, seed: int, autorefresh: Autorefresh
    ) -> tuple[Any, ...]:
        raise NotImplementedError
