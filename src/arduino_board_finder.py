# src/arduino_board_finder.py

from .cli_utils import run_cli_command

def get_available_boards(cli_path: str, config_path: str) -> list[str]:
    """
    Gets a list of all board names known by the installed cores.
    """
    success, data = run_cli_command(cli_path, config_path, ["board", "listall", "--format", "json"], expect_json=True)
    
    if not success:
        print(f"❌ Error fetching all available boards: {data}")
        return ["Error: Could not list boards"]

    if 'boards' in data and data.get('boards'):
        return sorted(list(set(b['name'] for b in data['boards'])))
    
    return ["Error: No boards found by listall command"]

def get_fqbn_by_name(cli_path: str, config_path: str, board_name: str) -> tuple[str | None, str | None]:
    """
    Finds the FQBN for a given board name.
    """
    success, data = run_cli_command(cli_path, config_path, ["board", "listall", "--format", "json"], expect_json=True)

    if not success or 'boards' not in data:
        return None, f"Could not retrieve board list to find FQBN for '{board_name}'"
    
    for board in data['boards']:
        if board.get('name') == board_name:
            return board.get('fqbn'), None

    return None, f"FQBN for '{board_name}' not found."