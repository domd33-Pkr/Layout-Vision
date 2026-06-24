import re
import time
import serial
from PySide6.QtCore import QThread, Signal

class SerialReaderThread(QThread):
    key_pressed_signal = Signal(int, bool)
    layer_changed_signal = Signal(int, bool)

    def __init__(self, port='/dev/ttyACM0', baudrate=115200, parent=None):
        super().__init__(parent)
        self.port = port
        self.baudrate = baudrate
        self.running = False
        self.pos_pattern = re.compile(r"position_state_changed: position (\d+) state (\d+)")
        self.layer_pattern = re.compile(r"layer_state_changed: layer (\d+) state (\d+)")

    def run(self):
        self.running = True
        while self.running:
            try:
                with serial.Serial(self.port, self.baudrate, timeout=1) as ser:
                    while self.running:
                        if ser.in_waiting:
                            line = ser.readline().decode('utf-8', errors='ignore').strip()
                            if not line:
                                continue
                            
                            # Match position
                            m_pos = self.pos_pattern.search(line)
                            if m_pos:
                                position = int(m_pos.group(1))
                                state = bool(int(m_pos.group(2)))
                                self.key_pressed_signal.emit(position, state)
                                continue
                            
                            # Match layer
                            m_layer = self.layer_pattern.search(line)
                            if m_layer:
                                layer = int(m_layer.group(1))
                                state = bool(int(m_layer.group(2)))
                                self.layer_changed_signal.emit(layer, state)
            except Exception as e:
                # Retry connection after a delay
                time.sleep(2)
                
    def stop(self):
        self.running = False
        self.wait()
