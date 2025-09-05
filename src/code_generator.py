# src/code_generator.py

def create_communication_map(code_block: dict) -> dict:
    comm_map = {}
    index = 0
    for name in sorted(code_block.get('shared_variable_names', [])):
        comm_map[name] = {"index": index, "type": "shared"}
        index += 1
    for pin_name in sorted(code_block.get('pin_states', {}).keys()):
        details = code_block['pin_states'][pin_name]
        if pin_name not in comm_map:
            comm_map[pin_name] = { "index": index, "type": details["type"], "pin_number": int(pin_name.split('_')[2]) }
            index += 1
    return comm_map

def generate_arduino_code(code_block: dict, cadence_ms: int, comm_map: dict) -> str:
    total_vars = len(comm_map)
    has_comms = total_vars > 0

    control_code = ""
    if has_comms:
        control_array_def = f"int controlValues[{total_vars}];"
        apply_state_lines = ["void applyControlValues() {"]
        for name, details in comm_map.items():
            if details['type'] == 'digital':
                apply_state_lines.append(f"  digitalWrite({details['pin_number']}, controlValues[{details['index']}]);")
            elif details['type'] == 'analog':
                apply_state_lines.append(f"  analogWrite({details['pin_number']}, controlValues[{details['index']}]);")
        apply_state_lines.append("}")
        
        process_command_lines = [
            "void processSerialCommand() {",
            "  char command_type = serialBuffer[0];",
            "  if ((command_type != 'S' && command_type != 'G') || serialBuffer[1] != ':') return;",
            "  int index = atoi(serialBuffer + 2);",
            f"  if (index < 0 || index >= {total_vars}) return;",
            "",
            "  if (command_type == 'S') {",
            "    char* valueStr = strchr(serialBuffer + 2, ':');",
            "    if (!valueStr) return;",
            "    controlValues[index] = atoi(valueStr + 1);",
            "    Serial.print(\"OK:S:\"); Serial.println(index);",
            "  }",
            # THE FIX: This now handles 'G' requests for ALL variables, not just shared ones.
            " else if (command_type == 'G') {",
            "    Serial.print(\"R:\"); Serial.print(index); Serial.print(\":\"); Serial.println(controlValues[index]);",
            "  }",
            "}",
        ]
        
        control_code = f"""
#define SERIAL_BUFFER_SIZE 64
char serialBuffer[SERIAL_BUFFER_SIZE];
byte serialBufferPos = 0;
{control_array_def}
{'\n'.join(apply_state_lines)}
{'\n'.join(process_command_lines)}
void checkSerialInput() {{
  while (Serial.available() > 0) {{
    char inChar = Serial.read();
    if (inChar == '\\n' || inChar == '\\r') {{
      if (serialBufferPos > 0) {{
        serialBuffer[serialBufferPos] = '\\0';
        processSerialCommand();
        serialBufferPos = 0;
      }}
    }} else if (serialBufferPos < SERIAL_BUFFER_SIZE - 1) {{
      serialBuffer[serialBufferPos++] = inChar;
    }}
  }}
}}"""

    setup_lines = []
    if has_comms: setup_lines.append("  Serial.begin(9600);")
    for pin in sorted(list(code_block.get('setup_pins', set()))):
        setup_lines.append(f"  pinMode({pin}, OUTPUT);")
    for name, details in comm_map.items():
        initial_value = 0
        if details['type'] != 'shared' and name in code_block['pin_states']:
            val = code_block['pin_states'][name]['value']
            if isinstance(val, str) and val.upper() == 'HIGH': initial_value = 1
            elif isinstance(val, str) and val.upper() == 'LOW': initial_value = 0
            else: initial_value = val
        setup_lines.append(f"  controlValues[{details['index']}] = {initial_value}; // Initial state for {name}")

    loop_body = "  applyControlValues();" if has_comms else "// Empty loop"
    serial_check_call = "  checkSerialInput();" if has_comms else ""
    final_code = f"""
{control_code}
void setup() {{
{'\n'.join(setup_lines)}
}}
void loop() {{
{serial_check_call}
{loop_body}
}}"""
    return final_code.strip()