# __init__.py

from .nodes import ArduinoTargetNode # <-- NOM MIS À JOUR

# --- Mappings for ComfyUI ---

NODE_CLASS_MAPPINGS = {
    "ArduinoTarget": ArduinoTargetNode, # <-- NOM MIS À JOUR
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ArduinoTarget": "Define Arduino Target", # <-- NOM MIS À JOUR
}

print("...Custom Nodes: ComfyUI-Arduino loaded.")