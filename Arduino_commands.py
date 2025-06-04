import serial
import time

def Reset(Changeable_Consts):
    """
    Resets the Arduino by toggling the DTR signal.
    
    Parameters:
    - arduino_port: The port where Arduino is connected (e.g., '/dev/ttyUSB0' or 'COM3')
    - baud_rate: The baud rate for serial communication (default: 9600)
    - delay_time: Time to wait during reset (default: 1 second)
    """
    ser = Changeable_Consts[0]
    delay_time=3
    try:        
        # Reset Arduino by toggling the DTR signal
        ser.dtr = False  # Set DTR to low (this resets the Arduino)
        time.sleep(delay_time)  # Wait for a short time to allow reset
        ser.dtr = True   # Set DTR back to high to allow Arduino to start running again
        arduino_port = ser.port
        response =f"Arduino reset via {arduino_port}"
        
        # Close the serial connection
        ser.close()
        time.sleep(delay_time)
        
        
    except serial.SerialException as e:
        response = "Error: Could not open the port {arduino_port}. {e}"
    except Exception as e:
        response =f"Error: An unexpected error occurred: {e}"

    print(response)

# Example usage:
#Reset()  # Adjust the port to your Arduino's port
