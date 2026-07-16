import re
import time
import serial
import os
from datetime import datetime
from PySide6.QtCore import QThread, Signal

def log_debug(msg):
    try:
        with open('/home/dominic/Documents/Claviers/Layout Vision/layout_vision_debug.log', 'a') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] {msg}\n")
    except Exception:
        pass

class SerialReaderThread(QThread):
    key_pressed_signal = Signal(int, bool)
    layer_changed_signal = Signal(int, bool)

    def __init__(self, port='/dev/ttyACM0', baudrate=115200, parent=None):
        super().__init__(parent)
        self.port = port
        self.baudrate = baudrate
        self.running = False
        self.pos_pattern = re.compile(r"(?:position_state_changed: position (\d+) state (\d+))|(?:position: (\d+), pressed: (true|false))")
        self.layer_pattern = re.compile(r"(?:layer_state_changed: layer (\d+) state (\d+|true|false))|(?:layer_changed: layer (\d+) state (\d+|true|false))")

    def get_port(self):
        for p in ['/dev/ttyACM1', '/dev/ttyACM0']:
            if os.path.exists(p):
                return p
        return self.port

    def run(self):
        self.running = True
        log_debug("[SERIAL] Starting thread loop...")
        while self.running:
            try:
                active_port = self.get_port()
                log_debug(f"[SERIAL] Attempting connection to {active_port}")
                with serial.Serial(active_port, self.baudrate, timeout=1) as ser:
                    log_debug(f"[SERIAL] Connected to {active_port}")
                    while self.running:
                        if ser.in_waiting:
                            line = ser.readline().decode('utf-8', errors='ignore').strip()
                            if not line:
                                continue
                            
                            # Log ZMK lines to see what we're receiving
                            if "zmk:" in line or "layer" in line or "position" in line:
                                log_debug(f"[SERIAL] Read line: {line}")
                            
                            # Match position
                            m_pos = self.pos_pattern.search(line)
                            if m_pos:
                                if m_pos.group(1) is not None:
                                    position = int(m_pos.group(1))
                                    state = bool(int(m_pos.group(2)))
                                else:
                                    position = int(m_pos.group(3))
                                    state = True if m_pos.group(4) == 'true' else False
                                log_debug(f"[SERIAL] Match position: position={position}, state={state}")
                                self.key_pressed_signal.emit(position, state)
                                continue
                            
                            # Match layer
                            m_layer = self.layer_pattern.search(line)
                            if m_layer:
                                if m_layer.group(1) is not None:
                                    layer = int(m_layer.group(1))
                                    state_str = m_layer.group(2)
                                else:
                                    layer = int(m_layer.group(3))
                                    state_str = m_layer.group(4)
                                state = state_str.lower() in ('1', 'true')
                                log_debug(f"[SERIAL] Match layer: layer={layer}, state={state}")
                                self.layer_changed_signal.emit(layer, state)
            except Exception as e:
                log_debug(f"[SERIAL] Exception: {e}")
                # Retry connection after a delay
                time.sleep(2)
                
    def stop(self):
        self.running = False
        log_debug("[SERIAL] Stopping thread...")
        self.wait()
