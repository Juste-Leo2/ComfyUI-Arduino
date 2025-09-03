# src/cli_utils.py

import subprocess
import json
import os

def run_cli_command(cli_path: str, config_path: str, args: list, expect_json=False):
    """
    Runs a command with arduino-cli using a specific config file.
    """
    # Prepend the config file argument to every command
    command = [cli_path, "--config-file", config_path] + args
    
    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    try:
        # We don't print the full command anymore to reduce log spam
        # print(f"   Running command: {' '.join(command)}")
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            startupinfo=startupinfo
        )
        
        stdout = process.stdout.strip()
        
        if expect_json:
            return True, json.loads(stdout) if stdout else {}
        
        return True, stdout

    except subprocess.CalledProcessError as e:
        error_message = f"Command failed: {' '.join(args)}\n" \
                        f"Stderr: {e.stderr.strip()}"
        return False, error_message
    except Exception as e:
        return False, f"An unexpected error occurred running {' '.join(args)}: {e}"