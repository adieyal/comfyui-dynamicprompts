import logging

from dynamicprompts.generators import FeelingLuckyGenerator, RandomPromptGenerator
from dynamicprompts.sampling_context import SamplingContext

from .sampler import DPAbstractSamplerNode

logger = logging.getLogger(__name__)


class DPFeelingLucky(DPAbstractSamplerNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._random_generator = RandomPromptGenerator(
            wildcard_manager=self._wildcard_manager,
        )
        self._prompt_generator = FeelingLuckyGenerator(generator=self._random_generator)

    def get_prompt(self, text: str, seed: int, autorefresh: str) -> tuple[str]:
        """
        Main entrypoint for this node.
        Using the sampling context, generate a new prompt.
        """

        if text.strip() == "":
            self._current_prompt = text
            self._last_generated_prompt = ""
            return ("",)

        self.prepare_generation(text, seed)

        if self.can_reuse_prompt(autorefresh):
            return (self._last_generated_prompt,)

        try:
            prompt = self._prompt_generator.generate(text, 1)[0]

            self._last_generated_prompt = str(prompt)

            return (self._last_generated_prompt,)
        except Exception as e:
            logger.exception(e)
            return ("",)

    @property
    def context(self) -> SamplingContext:
        return self._random_generator._context
