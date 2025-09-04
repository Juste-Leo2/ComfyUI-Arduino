# nodes.py

import os
from .src.arduino_installer import setup_arduino_cli
from .src.arduino_board_finder import get_available_boards, get_fqbn_by_name
from .src.arduino_actions import compile_and_upload_sketch # <-- NOUVEL IMPORT
import serial.tools.list_ports

def list_physical_ports():
    ports = serial.tools.list_ports.comports()
    return [f"{p.device} - {p.description}" for p in ports] if ports else ["No COM ports found"]

# --------------------------------------------------------------------
# -- GLOBAL INITIALIZATION (RUNS ONCE AT STARTUP) --------------------
# --------------------------------------------------------------------
NODE_DIR = os.path.dirname(os.path.abspath(__file__))
print("--- Initializing ComfyUI-Arduino: Setting up arduino-cli ---")

# The setup function now returns all the paths we need or an error
ARDUINO_CLI_PATH, ARDUINO_CONFIG_PATH, SETUP_ERROR = setup_arduino_cli(NODE_DIR)

AVAILABLE_BOARDS = ["Error: CLI setup failed"]
AVAILABLE_PORTS = ["Error: pyserial missing or failed"]

if SETUP_ERROR is None:
    print("--- Fetching board lists and COM ports ---")
    AVAILABLE_BOARDS = get_available_boards(ARDUINO_CLI_PATH, ARDUINO_CONFIG_PATH)
    AVAILABLE_PORTS = list_physical_ports()
    print(f"   Found {len(AVAILABLE_BOARDS)} board types and {len(AVAILABLE_PORTS)} COM ports.")
    print("--- ComfyUI-Arduino initialized successfully. ---")
else:
    print(f"FATAL: ComfyUI-Arduino setup failed: {SETUP_ERROR}")

# --------------------------------------------------------------------
# -- NODE: DEFINE ARDUINO TARGET -------------------------------------
# --------------------------------------------------------------------
class ArduinoTargetNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "board_name": (AVAILABLE_BOARDS, ),
                "port_str": (AVAILABLE_PORTS, ),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("port", "fqbn", "status")
    FUNCTION = "define_target"
    CATEGORY = "Arduino"

    def define_target(self, board_name, port_str):
        if SETUP_ERROR is not None:
            return ("ERROR", "ERROR", f"Setup failed: {SETUP_ERROR}")
        
        port = port_str.split(' ')[0]
        print(f"--- Defining target: Board '{board_name}' on port '{port}' ---")
        
        fqbn, error = get_fqbn_by_name(ARDUINO_CLI_PATH, ARDUINO_CONFIG_PATH, board_name)
        
        if error:
            return ("ERROR", "ERROR", error)
        
        status_message = f"✅ Target defined: {board_name} ({fqbn}) on {port}"
        return (port, fqbn, status_message)

# --------------------------------------------------------------------
# -- NODE: ARDUINO CODE INPUT ----------------------------------------
# --------------------------------------------------------------------
class ArduinoCodeNode:
    @classmethod
    def INPUT_TYPES(s):
        default_code = "void setup() {\n  // put your setup code here, to run once:\n\n}\n\nvoid loop() {\n  // put your main code here, to run repeatedly:\n\n}"
        return {
            "required": {
                "code": ("STRING", {"multiline": True, "default": default_code}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("code",)
    FUNCTION = "get_code"
    CATEGORY = "Arduino"

    def get_code(self, code):
        return (code,)

# --------------------------------------------------------------------
# -- NODE: COMPILE & UPLOAD SKETCH -----------------------------------
# --------------------------------------------------------------------
class ArduinoCompileUploadNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "port": ("STRING", {"forceInput": True}),
                "fqbn": ("STRING", {"forceInput": True}),
                "code": ("STRING", {"forceInput": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status",)
    FUNCTION = "compile_and_upload"
    CATEGORY = "Arduino"

    def compile_and_upload(self, port, fqbn, code):
        # Step 1: Node-level validation
        if SETUP_ERROR is not None:
            return (f"❌ ERROR: Setup failed: {SETUP_ERROR}",)
        if port == "ERROR" or fqbn == "ERROR":
            return ("❌ ERROR: Invalid target. Check 'Define Arduino Target' node.",)

        print(f"--- Arduino: Starting compile & upload for {fqbn} on {port} ---")
        
        # Step 2: Call the backend logic function
        success, message = compile_and_upload_sketch(
            cli_path=ARDUINO_CLI_PATH,
            config_path=ARDUINO_CONFIG_PATH,
            port=port,
            fqbn=fqbn,
            code=code
        )
        
        print(f"--- Arduino: Process finished. ---")
        
        # Step 3: Return the result from the logic function
        return (message,)