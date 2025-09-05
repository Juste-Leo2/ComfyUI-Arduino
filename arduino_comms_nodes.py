# arduino_comms_nodes.py

from .src.serial_communicator import send_and_receive
from .nodes import ARDUINO_PROFILES

class ArduinoSenderNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "port": ("STRING", {"default": "COM3"}),
                "variable_name": ("STRING", {"default": "state_pin_13"}),
                "value": ("STRING", {"default": "HIGH", "multiline": False}),
            },
        }
    RETURN_TYPES = ("STRING",); RETURN_NAMES = ("status",); FUNCTION = "send_data"; CATEGORY = "Arduino/Communication"

    def send_data(self, port, variable_name, value):
        if port not in ARDUINO_PROFILES:
            return (f"❌ ERROR: No profile for {port}. Upload code first.",)
        
        comm_map = ARDUINO_PROFILES[port].get("comm_map", {})
        if variable_name not in comm_map:
            return (f"❌ ERROR: Variable '{variable_name}' not found in profile for {port}.",)

        details = comm_map[variable_name]
        variable_index = details["index"]
        
        try:
            value_str = str(value).strip().upper()
            if value_str == "HIGH": int_value = 1
            elif value_str == "LOW": int_value = 0
            else: int_value = int(float(value_str))
        except (ValueError, TypeError):
            return (f"❌ ERROR: Invalid value '{value}'. Must be an integer, HIGH, or LOW.",)

        command = f"S:{variable_index}:{int_value}\n"
        success, response = send_and_receive(port, command)
        
        if not success: return (f"❌ ERROR: {response}",)
        
        expected_ack = f"OK:S:{variable_index}"
        if response.startswith(expected_ack):
            return (f"✅ Sent {value} to '{variable_name}'.",)
        else:
            return (f"⚠️ UNEXPECTED RESPONSE: {response}",)

class ArduinoReceiverNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "port": ("STRING", {"default": "COM3"}),
                "variable_name": ("STRING", {"default": "my_variable"}),
            },
            "optional": { "trigger": ("*",), }
        }
    RETURN_TYPES = ("INT", "STRING",); RETURN_NAMES = ("value", "status",); FUNCTION = "receive_data"; CATEGORY = "Arduino/Communication"

    def receive_data(self, port, variable_name, trigger=None):
        if port not in ARDUINO_PROFILES:
            return (-1, f"❌ ERROR: No profile for {port}. Upload code first.",)

        comm_map = ARDUINO_PROFILES[port].get("comm_map", {})
        if variable_name not in comm_map:
            return (-1, f"❌ ERROR: Variable '{variable_name}' not found in profile for {port}.",)
        
        # THE FIX: This entire 'if' block is removed to allow reading any variable type.
        # if details['type'] != 'shared':
        #      return (-1, f"❌ ERROR: Can only receive from general-purpose variables...")

        details = comm_map[variable_name]
        variable_index = details["index"]
        command = f"G:{variable_index}\n"
        success, response = send_and_receive(port, command)

        if not success: return (-1, f"❌ ERROR: {response}",)

        parts = response.split(':')
        if len(parts) == 3 and parts[0] == 'R' and parts[1] == str(variable_index):
            try:
                value = int(parts[2])
                return (value, f"✅ Received {value} from '{variable_name}'.")
            except ValueError:
                return (-1, f"⚠️ INVALID VALUE in response: {response}")
        else:
            return (-1, f"⚠️ UNEXPECTED RESPONSE: {response}")