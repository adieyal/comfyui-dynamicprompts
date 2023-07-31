from dynamicprompts.commands.base import SamplingMethod
from dynamicprompts.sampling_context import SamplingContext
from dynamicprompts.wildcards import WildcardManager

from .sampler import DPAbstractSamplerNode


class DPCombinatorialGenerator(DPAbstractSamplerNode):
    def _get_context(self, wildcard_manager: WildcardManager):
        self._context = SamplingContext(
            wildcard_manager=wildcard_manager,
            default_sampling_method=SamplingMethod.COMBINATORIAL,
        )
