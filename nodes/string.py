class DPMultilineString:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string": ("STRING", {"multiline": True, "dynamicPrompts": False}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "run"
    CATEGORY = "Dynamic Prompts"

    CATEGORY = "utils"

    def run(self, string) -> tuple[str]:
        return (string,)
