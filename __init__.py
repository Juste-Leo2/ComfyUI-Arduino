# __init__.py

from .nodes import ArduinoTargetNode, ArduinoCodeNode, ArduinoCompileUploadNode

# --- Mappings for ComfyUI ---

NODE_CLASS_MAPPINGS = {
    "ArduinoTarget": ArduinoTargetNode,
    "ArduinoCode": ArduinoCodeNode,
    "ArduinoCompileUpload": ArduinoCompileUploadNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ArduinoTarget": "Define Arduino Target",
    "ArduinoCode": "Arduino Code",
    "ArduinoCompileUpload": "Compile & Upload to Arduino",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

print("...Custom Nodes: ComfyUI-Arduino loaded.")