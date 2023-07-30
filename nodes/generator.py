from abc import ABC, abstractmethod


class DPGeneratorNode(ABC):
    RETURN_TYPES = ("STRING",)
    FUNCTION = "get_prompt"
    CATEGORY = "Dynamic Prompts"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("PROMPT", {"multiline": True}),
                "autorefresh": (["Yes", "No"],),
            },
        }

    @classmethod
    def IS_CHANGED(cls, text, autorefresh):
        # Force re-evaluation of the node
        if autorefresh == "Yes":
            return float("NaN")

    def get_prompt(self, text: str, autorefresh: str) -> tuple[str]:
        prompt = self.generate_prompt(text)
        print(f"Prompt: {prompt}")

        return (prompt,)

    @abstractmethod
    def generate_prompt(self, text: str) -> str:
        ...
