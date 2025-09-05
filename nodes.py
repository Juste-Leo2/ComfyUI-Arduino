# nodes.py

import os
from .src.arduino_installer import setup_arduino_cli
from .src.arduino_board_finder import get_available_boards, get_fqbn_by_name
from .src.arduino_actions import compile_and_upload_sketch
from .src.code_generator import generate_arduino_code, create_communication_map
import serial.tools.list_ports

from .arduino_native_nodes import ARDUINO_CODE_BLOCK

# --- GLOBAL PROFILE STORAGE ---
ARDUINO_PROFILES = {}

# --- Global Initialization (unchanged) ---
def list_physical_ports():
    ports = serial.tools.list_ports.comports()
    return [f"{p.device} - {p.description}" for p in ports] if ports else ["No COM ports found"]
NODE_DIR = os.path.dirname(os.path.abspath(__file__))
print("--- Initializing ComfyUI-Arduino: Setting up arduino-cli ---")
ARDUINO_CLI_PATH, ARDUINO_CONFIG_PATH, SETUP_ERROR = setup_arduino_cli(NODE_DIR)
AVAILABLE_BOARDS = ["Error: CLI setup failed"]
AVAILABLE_PORTS = ["Error: pyserial missing or failed"]
if SETUP_ERROR is None:
    print("--- Fetching board lists and COM ports ---")
    AVAILABLE_BOARDS = get_available_boards(ARDUINO_CLI_PATH, ARDUINO_CONFIG_PATH)
    AVAILABLE_PORTS = list_physical_ports()
else:
    print(f"FATAL: ComfyUI-Arduino setup failed: {SETUP_ERROR}")

# --- Node Definitions ---

class ArduinoTargetNode:
    @classmethod
    def INPUT_TYPES(s):
        return { "required": { "board_name": (AVAILABLE_BOARDS, ), "port_str": (AVAILABLE_PORTS, ), } }
    RETURN_TYPES = ("STRING", "STRING", "STRING"); RETURN_NAMES = ("port", "fqbn", "status"); FUNCTION = "define_target"; CATEGORY = "Arduino/Build"
    def define_target(self, board_name, port_str):
        if SETUP_ERROR is not None: return ("ERROR", "ERROR", f"Setup failed: {SETUP_ERROR}")
        port = port_str.split(' ')[0]
        fqbn, error = get_fqbn_by_name(ARDUINO_CLI_PATH, ARDUINO_CONFIG_PATH, board_name)
        if error: return ("ERROR", "ERROR", error)
        status_message = f"✅ Target defined: {board_name} ({fqbn}) on {port}"
        return (port, fqbn, status_message)

class ArduinoCompileUploadNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "port": ("STRING", {"forceInput": True}),
                "fqbn": ("STRING", {"forceInput": True}),
                "code_block": (ARDUINO_CODE_BLOCK, {}),
                "cadence_ms": ("INT", {"default": 10, "min": 1}),
            }
        }
    RETURN_TYPES = ("STRING",); RETURN_NAMES = ("status",); FUNCTION = "compile_and_upload"; CATEGORY = "Arduino/Build"
    
    def compile_and_upload(self, port, fqbn, code_block, cadence_ms):
        if SETUP_ERROR is not None: return (f"❌ ERROR: Setup failed: {SETUP_ERROR}",)
        if port == "ERROR" or fqbn == "ERROR": return ("❌ ERROR: Invalid target.",)

        comm_map = create_communication_map(code_block)
        final_code = generate_arduino_code(code_block, cadence_ms, comm_map)
        
        print(f"--- Arduino: Starting compile & upload for {fqbn} on {port} ---")
        
        success, message = compile_and_upload_sketch(
            cli_path=ARDUINO_CLI_PATH, config_path=ARDUINO_CONFIG_PATH,
            port=port, fqbn=fqbn, code=final_code
        )
        
        if success:
            profile = { "port": port, "fqbn": fqbn, "comm_map": comm_map }
            global ARDUINO_PROFILES
            ARDUINO_PROFILES[port] = profile
            print(f"--- Arduino: Profile for port {port} created and stored. ---")
            message += f"\n✅ Profile ready for port {port}."
        
        return (message,)