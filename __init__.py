# __init__.py

from .nodes import (
    ArduinoTargetNode, 
    ArduinoCompileUploadNode
)
from .arduino_native_nodes import (
    ArduinoCreateVariableNode, # <-- NOUVEAU pour la flexibilité
    ArduinoDigitalWriteNode, 
    ArduinoAnalogWriteNode, 
    ArduinoDelayNode,
    ArduinoVariableInfoNode # <-- NOUVEAU pour l'info
)
from .arduino_comms_nodes import (
    ArduinoSenderNode, 
    ArduinoReceiverNode
)


# --- Mappings for ComfyUI ---
NODE_CLASS_MAPPINGS = {
    # Workflow 1: Build
    "ArduinoTarget": ArduinoTargetNode,
    "ArduinoCreateVariable": ArduinoCreateVariableNode,
    "ArduinoDigitalWrite": ArduinoDigitalWriteNode,
    "ArduinoAnalogWrite": ArduinoAnalogWriteNode,
    "ArduinoDelay": ArduinoDelayNode,
    "ArduinoVariableInfo": ArduinoVariableInfoNode,
    "ArduinoCompileUpload": ArduinoCompileUploadNode,
    
    # Workflow 2: Communication
    "ArduinoSender": ArduinoSenderNode,
    "ArduinoReceiver": ArduinoReceiverNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    # Workflow 1
    "ArduinoTarget": "1. Define Arduino Target",
    "ArduinoCreateVariable": "Native: Create Variable",
    "ArduinoDigitalWrite": "Native: DigitalWrite",
    "ArduinoAnalogWrite": "Native: AnalogWrite (PWM)",
    "ArduinoDelay": "Native: Delay (Non-Blocking)",
    "ArduinoVariableInfo": "Show Variable Info",
    "ArduinoCompileUpload": "2. Compile & Upload",

    # Workflow 2
    "ArduinoSender": "Send to Arduino (by Port)",
    "ArduinoReceiver": "Receive from Arduino (by Port)",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

print("...Custom Nodes: ComfyUI-Arduino loaded.")