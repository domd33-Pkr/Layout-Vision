import serial
import time
import sys

def check_port(port):
    print(f"Testing {port}...")
    try:
        with serial.Serial(port, 115200, timeout=1) as ser:
            start_time = time.time()
            # Wait for 3 seconds to see if anything comes out
            while time.time() - start_time < 3:
                if ser.in_waiting:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    print(f"[{port}] {line}")
    except Exception as e:
        print(f"Error on {port}: {e}")

check_port('/dev/ttyACM0')
check_port('/dev/ttyACM1')
