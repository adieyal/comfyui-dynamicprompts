import logging

from dynamicprompts.generators import RandomPromptGenerator
from dynamicprompts.generators.magicprompt import MagicPromptGenerator
from dynamicprompts.sampling_context import SamplingContext

from .sampler import DPAbstractSamplerNode

logger = logging.getLogger(__name__)


class DPMagicPrompt(DPAbstractSamplerNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._random_generator = RandomPromptGenerator(
            wildcard_manager=self._wildcard_manager,
        )
        self._prompt_generator = MagicPromptGenerator(
            prompt_generator=self._random_generator,
        )

    def get_prompt(self, text: str, seed: int, autorefresh: str) -> tuple[str]:
        """
        Main entrypoint for this node.
        Using the sampling context, generate a new prompt.
        """

        if seed > 0:
            self.context.rand.seed(seed)

        if text.strip() == "":
            return ("",)

        try:
            prompt = self._prompt_generator.generate(text, 1)[0]

            return (str(prompt),)
        except Exception as e:
            logger.exception(e)
            return ("",)

    @property
    def context(self) -> SamplingContext:
        return self._random_generator._context
