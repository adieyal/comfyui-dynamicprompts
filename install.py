import shutil
from pathlib import Path

comfy_path = Path(__file__).parent.parent.parent
extension_path = Path(__file__).parent
js_path = comfy_path / "web" / "extensions"


def copy_web_extensions():
    shutil.copy(extension_path / "web-extensions/dp.js", str(js_path))


copy_web_extensions()
