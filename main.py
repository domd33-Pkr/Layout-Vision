import sys
import os
import signal
from PySide6.QtWidgets import QApplication
from serial_reader import SerialReaderThread
from ui_overlay import LayoutOverlay

def main():
    # Allow Ctrl+C to kill the Qt application gracefully
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    # Force XWayland instead of native Wayland to ensure 
    # FramelessWindowHint and WindowStaysOnTopHint are respected
    os.environ["QT_QPA_PLATFORM"] = "xcb"
    
    app = QApplication(sys.argv)
    
    # Path to layout data
    json_path = '/home/dominic/Documents/Claviers/Key Configurator/Archives/keyboard_layout_updated.json'
    
    if not os.path.exists(json_path):
        print(f"Error: Could not find layout file at {json_path}")
        sys.exit(1)
            
    overlay = LayoutOverlay(json_path)
    overlay.show()
    
    # Configure the serial port for Linux ZMK USB Debug Logging
    serial_port = '/dev/ttyACM0'
    
    # Start the background thread to read the serial stream
    reader_thread = SerialReaderThread(port=serial_port)
    reader_thread.key_pressed_signal.connect(overlay.on_key_pressed)
    reader_thread.layer_changed_signal.connect(overlay.on_layer_changed)
    reader_thread.start()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
