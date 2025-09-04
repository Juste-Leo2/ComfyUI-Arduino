# src/arduino_actions.py

import os
import shutil
import tempfile
from .cli_utils import run_cli_command

def compile_and_upload_sketch(cli_path: str, config_path: str, port: str, fqbn: str, code: str) -> tuple[bool, str]:
    """
    Handles the entire process of compiling and uploading an Arduino sketch.

    Args:
        cli_path: Path to the arduino-cli executable.
        config_path: Path to the arduino-cli.yaml config file.
        port: The COM port to upload to (e.g., "COM3").
        fqbn: The Fully Qualified Board Name (e.g., "arduino:avr:uno").
        code: A string containing the Arduino C++ code.

    Returns:
        A tuple containing:
        - bool: True if successful, False otherwise.
        - str: A status message detailing the outcome.
    """
    # Arduino CLI requires the .ino file to be in a folder with the same name.
    # We create a temporary directory for this.
    temp_dir = tempfile.mkdtemp()
    sketch_name = os.path.basename(temp_dir)
    sketch_path = os.path.join(temp_dir, f"{sketch_name}.ino")

    try:
        # 1. Write the code to the temporary .ino file
        with open(sketch_path, 'w', encoding='utf-8') as f:
            f.write(code)
        print(f"   - Temporary sketch created at {sketch_path}")

        # 2. Compile the sketch
        print(f"   - Compiling for board {fqbn}...")
        compile_args = ["compile", "--fqbn", fqbn, temp_dir]
        success, result = run_cli_command(cli_path, config_path, compile_args)
        if not success:
            error_msg = f"❌ Compilation failed: {result}"
            print(f"   - {error_msg}")
            return False, error_msg
        print("   - ✅ Compilation successful.")

        # 3. Upload the sketch
        print(f"   - Uploading to port {port}...")
        upload_args = ["upload", "-p", port, "--fqbn", fqbn, temp_dir]
        success, result = run_cli_command(cli_path, config_path, upload_args)
        if not success:
            error_msg = f"❌ Upload failed: {result}"
            print(f"   - {error_msg}")
            return False, error_msg
        
        status_message = f"✅✅✅ Upload to {fqbn} on {port} successful!"
        print(f"   - {status_message}")
        return True, status_message

    finally:
        # 4. Clean up the temporary directory, regardless of outcome
        print(f"   - Cleaning up temporary sketch directory: {temp_dir}")
        shutil.rmtree(temp_dir)