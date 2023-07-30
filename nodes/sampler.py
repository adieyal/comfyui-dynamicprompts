import logging
from abc import ABC, abstractmethod
from pathlib import Path

from dynamicprompts.wildcards import WildcardManager

logger = logging.getLogger(__name__)


class DPAbstractSamplerNode(ABC):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("PROMPT", {"dynamicPrompts": False, "multiline": True}),
            },
        }

    @classmethod
    def IS_CHANGED(cls, text):
        # Force re-evaluation of the node
        return float("NaN")

    RETURN_TYPES = ("STRING",)
    FUNCTION = "get_prompt"
    CATEGORY = "Dynamic Prompts"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        wildcards_folder = self._find_wildcards_folder()
        self._wildcard_manager = WildcardManager(path=wildcards_folder)
        self._sampling_context = self._get_context(self._wildcard_manager)
        self._current_prompt = None

    def _find_wildcards_folder(self):
        wildcards_folder = Path("wildcards")
        if wildcards_folder.exists():
            return wildcards_folder

        wildcards_folder = Path(__file__).parent / "wildcards"
        if wildcards_folder.exists():
            return wildcards_folder

        return None

    def _get_next_prompt(self):
        """
        Get the next prompt from the prompts generator.
        """
        try:
            return next(self._prompts)
        except StopIteration:
            self._prompts = self._context.sample_prompts(self._current_prompt)
            try:
                return next(self._prompts)
            except StopIteration:
                logger.exception("No more prompts to generate!")
                return ""

    def get_prompt(self, text: str) -> str:
        """
        Using the sampling context, generate a new prompt.
        """
        if text.strip() == "":
            return ("",)

        if self._current_prompt != text:
            self._current_prompt = text
            self._prompts = self._context.sample_prompts(self._current_prompt)

        if self._prompts is None:
            logger.exception("Prompts is None!")
            return ("",)

        new_prompt = self._get_next_prompt()
        logger.info(f"New prompt: {new_prompt}")

        logger.info(f"Prompt: {new_prompt}")
        print(f"Prompt: {new_prompt}")
        return (new_prompt,)

    @abstractmethod
    def _get_context(self, wildcard_manager: WildcardManager = None):
        ...
