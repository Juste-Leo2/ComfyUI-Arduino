# src/serial_communicator.py

import serial
import time

def send_and_receive(port: str, command: str, timeout: float = 2.0) -> tuple[bool, str]:
    """
    Opens a serial port, sends a command, and waits for a single line response.
    
    Args:
        port: The COM port to connect to (e.g., "COM3").
        command: The command string to send (must end with '\\n').
        timeout: Time in seconds to wait for a response.

    Returns:
        A tuple (success, message). On success, message is the response from the device.
        On failure, message is an error description.
    """
    ser = None # Initialize ser to None
    try:
        # --- THE FINAL FIX: A MORE ROBUST WAY TO OPEN THE PORT ---
        # 1. Create the serial object without opening it immediately.
        ser = serial.Serial()
        
        # 2. Configure all parameters, including the port and baudrate.
        ser.port = port
        ser.baudrate = 9600
        ser.timeout = 0.1
        
        # 3. Set dtr to False *before* opening. This prevents the auto-reset signal.
        ser.dtr = False
        
        # 4. Now, open the port. The connection is established with DTR already low.
        ser.open()
        
        # A small delay after opening is still good practice.
        time.sleep(0.1) 
        
        ser.reset_input_buffer()
        ser.reset_output_buffer()

        ser.write(command.encode('utf-8'))
        
        # Add a tiny delay to give the Arduino time to process the command
        # before we start waiting for the reply.
        time.sleep(0.05)

        start_time = time.time()
        while time.time() - start_time < timeout:
            if ser.in_waiting > 0:
                response = ser.readline().decode('utf-8').strip()
                if response:
                    return True, response
        
        return False, f"Timeout: No response from {port} after {timeout}s."

    except serial.SerialException as e:
        return False, f"Serial Error on port {port}: {e}"
    except Exception as e:
        return False, f"An unexpected error occurred: {e}"
    finally:
        # Ensure the port is always closed, even if an error occurs.
        if ser and ser.is_open:
            ser.close()