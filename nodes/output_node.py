from __future__ import annotations

from typing import Any


class OutputString:
    """Kept so old workflows load. The frontend shows no text for it; use ComfyUI's Preview Any."""

    DEPRECATED = True

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, dict[str, tuple[Any, ...]]]:
        return {
            "required": {
                "text": ("STRING", {}),
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "output_string"

    OUTPUT_NODE = True

    CATEGORY = "utils"

    def output_string(self, text: str) -> dict[str, dict[str, list[str]]]:
        return {"ui": {"text": [text]}}
