from __future__ import annotations

import logging
from abc import ABC, abstractproperty
from collections.abc import Iterable
from pathlib import Path

from dynamicprompts.sampling_context import SamplingContext
from dynamicprompts.wildcards import WildcardManager

logger = logging.getLogger(__name__)


class DPAbstractSamplerNode(ABC):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "dynamicPrompts": False}),
                "seed": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 0xFFFFFFFFFFFFFFFF,
                        "control_after_generate": "fixed",
                        "display": "number",
                    },
                ),
                "autorefresh": (["Yes", "No"], {"default": "No"}),
            },
        }

    @classmethod
    def IS_CHANGED(cls, text: str, seed: int, autorefresh: str):
        # Force re-evaluation of the node
        if autorefresh == "Yes":
            return float("NaN")

    RETURN_TYPES = ("STRING",)
    FUNCTION = "get_prompt"
    CATEGORY = "Dynamic Prompts"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        wildcards_folder = self._find_wildcards_folder()
        self._wildcard_manager = WildcardManager(path=wildcards_folder)
        self._current_prompt = None
        self._last_generated_prompt = None
        self._last_seed = None
        self._prompts = None

    def _find_wildcards_folder(self) -> Path | None:
        """
        Find the wildcards folder.
        First look in the comfy_dynamicprompts folder, then in the custom_nodes folder, then in the Comfui base folder.
        """
        from folder_paths import base_path, folder_names_and_paths

        wildcard_path = Path(base_path) / "wildcards"

        if wildcard_path.exists():
            return wildcard_path

        extension_path = (
            Path(folder_names_and_paths["custom_nodes"][0][0])
            / "comfyui-dynamicprompts"
        )
        wildcard_path = extension_path / "wildcards"
        wildcard_path.mkdir(parents=True, exist_ok=True)

        return wildcard_path

    def _get_next_prompt(self, prompts: Iterable[str], current_prompt: str) -> str:
        """
        Get the next prompt from the prompts generator.
        """
        try:
            return next(prompts)
        except (StopIteration, RuntimeError):
            self._prompts = self.context.sample_prompts(current_prompt)
            try:
                return next(self._prompts)
            except StopIteration:
                logger.exception("No more prompts to generate!")
                return ""

    def has_prompt_changed(self, text: str) -> bool:
        """
        Check if the prompt has changed.
        """
        return self._current_prompt != text

    def prepare_generation(self, text: str, seed: int) -> None:
        """
        Reset cached generation state only when inputs that define the prompt change.
        """
        prompt_changed = self.has_prompt_changed(text)
        seed_changed = self._last_seed != seed

        if prompt_changed:
            self._current_prompt = text

        if seed_changed:
            if seed > 0:
                self.context.rand.seed(seed)
            self._last_seed = seed

        if prompt_changed or seed_changed:
            self._prompts = None
            self._last_generated_prompt = None

    def can_reuse_prompt(self, autorefresh: str) -> bool:
        return autorefresh != "Yes" and self._last_generated_prompt is not None

    def get_prompt(self, text: str, seed: int, autorefresh: str) -> tuple[str]:
        """
        Main entrypoint for this node.
        Using the sampling context, generate a new prompt.
        """

        if text.strip() == "":
            self._current_prompt = text
            self._prompts = None
            self._last_generated_prompt = ""
            return ("",)

        self.prepare_generation(text, seed)

        if self.can_reuse_prompt(autorefresh):
            return (self._last_generated_prompt,)

        if self._prompts is None:
            self._prompts = self.context.sample_prompts(self._current_prompt)

        if self._prompts is None:
            logger.exception("Something went wrong. Prompts is None!")
            return ("",)

        if self._current_prompt is None:
            logger.exception("Something went wrong. Current prompt is None!")
            return ("",)

        new_prompt = self._get_next_prompt(self._prompts, self._current_prompt)
        print(f"New prompt: {new_prompt}")

        self._last_generated_prompt = str(new_prompt)

        return (self._last_generated_prompt,)

    @abstractproperty
    def context(self) -> SamplingContext:
        ...
