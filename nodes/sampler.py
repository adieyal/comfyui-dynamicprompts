from __future__ import annotations

from typing import Any, Literal

from .wildcards import change_key

Autorefresh = Literal["Yes", "No"]


class DPSeededNode:
    """Inputs and caching shared by the Random, Combinatorial and MagicPrompt nodes."""

    RETURN_TYPES: tuple[str, ...] = ("STRING",)
    FUNCTION = "get_prompt"
    CATEGORY = "Dynamic Prompts"

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, dict[str, tuple[Any, ...]]]:
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
        }

    @classmethod
    def IS_CHANGED(cls, text: str, seed: int, autorefresh: Autorefresh) -> float | str:
        if autorefresh == "Yes":
            return float("nan")
        return change_key(text, seed)
