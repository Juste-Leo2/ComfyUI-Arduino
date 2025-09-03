# src/arduino_installer.py

import os
import platform
import shutil
import requests
import zipfile
import tarfile
import io
import textwrap
from .cli_utils import run_cli_command

# --- Constants ---
BASE_URL = "https://downloads.arduino.cc/arduino-cli/arduino-cli_latest"
BIN_DIR_NAME = "bin"
DATA_DIR_NAME = "arduino_data"
CONFIG_FILE_NAME = "arduino-cli.yaml"
CORE_TO_INSTALL = "arduino:avr"

def get_platform_specific_url():
    system = platform.system()
    arch = platform.machine()
    if system == "Windows": return f"{BASE_URL}_Windows_64bit.zip"
    if system == "Linux":
        return f"{BASE_URL}_Linux_ARM64.tar.gz" if "aarch64" in arch or "arm64" in arch else f"{BASE_URL}_Linux_64bit.tar.gz"
    if system == "Darwin": # macOS
        return f"{BASE_URL}_macOS_ARM64.tar.gz" if "arm64" in arch else f"{BASE_URL}_macOS_64bit.tar.gz"
    raise NotImplementedError(f"Unsupported OS: {system} {arch}")

def get_cli_executable_path(install_dir: str) -> str:
    bin_dir = os.path.join(install_dir, BIN_DIR_NAME)
    executable_name = "arduino-cli.exe" if platform.system() == "Windows" else "arduino-cli"
    return os.path.join(bin_dir, executable_name)

def setup_arduino_cli(install_dir: str) -> tuple[str | None, str | None, str | None]:
    cli_path = get_cli_executable_path(install_dir)
    data_dir = os.path.join(install_dir, DATA_DIR_NAME)
    config_path = os.path.join(install_dir, CONFIG_FILE_NAME)

    if not os.path.exists(cli_path):
        print(" arduino-cli not found. Starting download and installation...")
        bin_dir = os.path.dirname(cli_path)
        if os.path.exists(bin_dir): shutil.rmtree(bin_dir)
        os.makedirs(bin_dir, exist_ok=True)
        try:
            url = get_platform_specific_url()
            print(f"   Downloading from: {url}")
            response = requests.get(url, stream=True); response.raise_for_status()
            print("   Extracting archive...")
            if url.endswith(".zip"):
                with zipfile.ZipFile(io.BytesIO(response.content)) as z: z.extractall(bin_dir)
            else:
                with tarfile.open(fileobj=io.BytesIO(response.content), mode="r:gz") as t: t.extractall(bin_dir)
            if platform.system() != "Windows": os.chmod(cli_path, 0o755)
            print(f"✅ arduino-cli installed successfully: {cli_path}")
        except Exception as e:
            return None, None, f"Critical error during arduino-cli download/extraction: {e}"

    if not os.path.exists(config_path):
        print(f"--- First time setup: Manually creating a clean arduino-cli.yaml ---")
        os.makedirs(data_dir, exist_ok=True)
        data_dir_fwd = data_dir.replace('\\', '/')
        config_content = textwrap.dedent(f"""
            directories:
              data: {data_dir_fwd}
              downloads: {data_dir_fwd}/downloads
              user: {data_dir_fwd}/user
        """).strip()
        try:
            with open(config_path, 'w') as f: f.write(config_content)
            print(f"   Local config file created at: {config_path}")
        except Exception as e:
            return None, None, f"Failed to write config file: {e}"
            
    print("--- Verifying arduino-cli core installation ---")
    success, data = run_cli_command(cli_path, config_path, ["core", "list", "--format", "json"], expect_json=True)
    if not success: return None, None, f"Error checking installed cores: {data}"
    
    # *** THE ONE AND ONLY FIX IS HERE ***
    # The key is 'platforms', not 'result'.
    core_list = data.get('platforms', []) if isinstance(data, dict) else []

    core_is_installed = any(CORE_TO_INSTALL in core.get('id', '') for core in core_list if isinstance(core, dict))

    if core_is_installed:
        print(f"✅ Core '{CORE_TO_INSTALL}' is already installed.")
    else:
        print(f"   Core '{CORE_TO_INSTALL}' not found. Installing...")
        print("   Updating core index... (This may take a moment)")
        success, res = run_cli_command(cli_path, config_path, ["core", "update-index"])
        if not success: return None, None, f"Error updating core index: {res}"

        print(f"   Installing core '{CORE_TO_INSTALL}'...")
        success, res = run_cli_command(cli_path, config_path, ["core", "install", CORE_TO_INSTALL])
        if not success: return None, None, f"Error installing core: {res}"
        print(f"✅ Core '{CORE_TO_INSTALL}' installed successfully.")

    return cli_path, config_path, None