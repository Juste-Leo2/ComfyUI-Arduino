# arduino_native_nodes.py

import copy
from .src.code_generator import create_communication_map

ARDUINO_CODE_BLOCK = "ARDUINO_CODE_BLOCK"

def create_empty_code_block():
    """Creates the base data structure for our Arduino code."""
    return {
        "setup_pins": set(),
        "setup_code": [],
        "loop_steps": [], # Kept for potential future use, but ignored by current generator
        "global_vars": [],
        "shared_variable_names": [],
        "pin_states": {},
    }

def _append_code_to_last_step(steps, code_line):
    if not steps or not isinstance(steps[-1], list):
        steps.append([])
    steps[-1].append(code_line)

class ArduinoCreateVariableNode:
    @classmethod
    def INPUT_TYPES(s):
        return { "required": { "variable_name": ("STRING", {"multiline": False, "default": "my_variable"}) }, "optional": { "code_in": (ARDUINO_CODE_BLOCK,), } }
    RETURN_TYPES = (ARDUINO_CODE_BLOCK,); RETURN_NAMES = ("code_out",); FUNCTION = "create_var"; CATEGORY = "Arduino/Native"
    def create_var(self, variable_name, code_in=None):
        if code_in is None: code_in = create_empty_code_block()
        new_code_block = copy.deepcopy(code_in)
        if variable_name not in new_code_block["shared_variable_names"]:
            new_code_block["shared_variable_names"].append(variable_name)
        return (new_code_block,)
        
class ArduinoVariableInfoNode:
    @classmethod
    def INPUT_TYPES(s):
        return { "required": { "code_block": (ARDUINO_CODE_BLOCK,), } }
    RETURN_TYPES = ("STRING",); RETURN_NAMES = ("info",); FUNCTION = "get_info"; CATEGORY = "Arduino/Build"
    def get_info(self, code_block):
        comm_map = create_communication_map(code_block)
        info = "--- Controllable Variables ---\n"
        if not comm_map:
            info += "None detected. Use DigitalWrite or Create Variable nodes."
        else:
            for name, details in comm_map.items():
                info += f"- {name} (type: {details['type']})\n"
        return (info,)

class ArduinoDigitalWriteNode:
    @classmethod
    def INPUT_TYPES(s):
        return { "required": { "pin": ("INT", {"default": 13, "min": 0}), "value": (["HIGH", "LOW"],), }, "optional": { "code_in": (ARDUINO_CODE_BLOCK,), } }
    RETURN_TYPES = (ARDUINO_CODE_BLOCK,); RETURN_NAMES = ("code_out",); FUNCTION = "generate_code"; CATEGORY = "Arduino/Native"
    def generate_code(self, pin, value, code_in=None):
        if code_in is None: code_in = create_empty_code_block()
        new_code_block = copy.deepcopy(code_in)
        new_code_block["setup_pins"].add(pin) 
        # RENAMING: Use state_pin_X as the variable name
        new_code_block["pin_states"][f"state_pin_{pin}"] = {"type": "digital", "value": value}
        # The node no longer adds code to the loop, it just defines the initial state.
        return (new_code_block,)

class ArduinoAnalogWriteNode:
    @classmethod
    def INPUT_TYPES(s):
        return { "required": { "pin": ("INT", {"default": 9, "min": 0}), "value": ("INT", {"default": 128, "min": 0, "max": 255}), }, "optional": { "code_in": (ARDUINO_CODE_BLOCK,), } }
    RETURN_TYPES = (ARDUINO_CODE_BLOCK,); RETURN_NAMES = ("code_out",); FUNCTION = "generate_code"; CATEGORY = "Arduino/Native"
    def generate_code(self, pin, value, code_in=None):
        if code_in is None: code_in = create_empty_code_block()
        new_code_block = copy.deepcopy(code_in)
        new_code_block["setup_pins"].add(pin)
        # RENAMING: Use state_pin_X as the variable name
        new_code_block["pin_states"][f"state_pin_{pin}"] = {"type": "analog", "value": value}
        return (new_code_block,)

class ArduinoDelayNode:
    @classmethod
    def INPUT_TYPES(s):
        return { "required": { "delay_ms": ("INT", {"default": 1000, "min": 0}), }, "optional": { "code_in": (ARDUINO_CODE_BLOCK,), } }
    RETURN_TYPES = (ARDUINO_CODE_BLOCK,); RETURN_NAMES = ("code_out",); FUNCTION = "generate_delay"; CATEGORY = "Arduino/Native"
    def generate_delay(self, delay_ms, code_in=None):
        # This node is now informational and doesn't affect the generated loop code.
        if code_in is None: code_in = create_empty_code_block()
        return (copy.deepcopy(code_in),)