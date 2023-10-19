from abc import ABC, abstractmethod


class DPGeneratorNode(ABC):
    RETURN_TYPES = ("STRING",)
    FUNCTION = "get_prompt"
    CATEGORY = "Dynamic Prompts"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "dynamicPrompts": False}),
                "seed": ("INT", {"default": 0, "display": "number"}),
                "autorefresh": (["Yes", "No"], {"default": "No"}),
            },
        }

    @classmethod
    def IS_CHANGED(cls, text, seed, autorefresh):
        # Force re-evaluation of the node
        if autorefresh == "Yes":
            return float("NaN")

    def get_prompt(self, text: str, seed: int, autorefresh: str) -> tuple[str]:
        prompt = self.generate_prompt(text, seed)
        print(f"Prompt: {prompt}")

        return (prompt,)

    @abstractmethod
    def generate_prompt(self, text: str, seed: int) -> str:
        ...
