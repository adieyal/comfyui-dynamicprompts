class OutputString:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string": ("STRING", {}),
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "output_string"

    OUTPUT_NODE = True

    CATEGORY = "utils"

    def output_string(self, string):
        return ({"ui": {"string": string}},)
