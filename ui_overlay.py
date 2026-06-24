import json
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication, QGraphicsView, QGraphicsScene, QGraphicsProxyWidget, QGraphicsRectItem
from PySide6.QtCore import Qt, QPoint, QRectF
from PySide6.QtGui import QColor, QPen, QBrush, QPainter

POSITIONS = {
    10: {"x": 12, "y": 130, "r": 0},
    8: {"x": 76, "y": 48, "r": 0},
    9: {"x": 76, "y": 112, "r": 0},
    6: {"x": 140, "y": 14, "r": 0},
    7: {"x": 140, "y": 78, "r": 0},
    4: {"x": 204, "y": 54, "r": 0},
    5: {"x": 204, "y": 118, "r": 0},
    3: {"x": 236, "y": 182, "r": 0},
    2: {"x": 306, "y": 190, "r": 12},
    1: {"x": 373, "y": 212, "r": 24},

    20: {"x": 373 + 510, "y": 130, "r": 0},
    18: {"x": 309 + 510, "y": 48, "r": 0},
    19: {"x": 309 + 510, "y": 112, "r": 0},
    16: {"x": 245 + 510, "y": 14, "r": 0},
    17: {"x": 245 + 510, "y": 78, "r": 0},
    14: {"x": 181 + 510, "y": 54, "r": 0},
    15: {"x": 181 + 510, "y": 118, "r": 0},
    13: {"x": 149 + 510, "y": 182, "r": 0},
    12: {"x": 79 + 510, "y": 190, "r": -12},
    11: {"x": 12 + 510, "y": 212, "r": -24},
}

class KeyWidget(QLabel):
    def __init__(self, key_data, parent=None):
        super().__init__(parent)
        self.key_data = key_data
        self.index = key_data['index']
        self.is_pressed = False
        self.current_layer = 0
        
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(64, 64)
        self.update_style()
        self.update_text()
        
    def update_text(self):
        layer_str = str(self.current_layer)
        bindings = self.key_data.get('bindings', {})
        # Fallback to layer 0 if binding not defined for current layer
        layer_bindings = bindings.get(layer_str, bindings.get("0", {}))
        
        tap = layer_bindings.get('tap', '')
        hold = layer_bindings.get('hold', '')
        
        # Clean up some ZMK specific codes for display
        if tap.startswith('&ht'):
            parts = tap.split(' ')
            tap = parts[-1] if len(parts) > 1 else tap
        elif tap.startswith('&kp') or tap.startswith('&mo') or tap.startswith('&mt'):
            tap = tap.replace('&kp', '').replace('&mo', 'L').replace('&mt', '').strip()
        elif tap.startswith('&mtl'):
            parts = tap.split(' ')
            tap = parts[-1] if len(parts) > 1 else tap
            
        if tap.startswith('LCTL('):
            tap = '^' + tap.split('(')[1].replace(')', '')
        if tap.startswith('RSFT(') or tap.startswith('LSFT(') or tap.startswith('RS(') or tap.startswith('LS('):
            tap = tap.split('(')[1].replace(')', '')

        if tap == '&trans':
            tap = '▽'
            
        text = tap
        if hold:
            if hold.startswith('RSFT(') or hold.startswith('LSFT(') or hold.startswith('RS(') or hold.startswith('LS('):
                hold = hold.split('(')[1].replace(')', '')
            text = f"{tap}\n-\n{hold}"
            
        self.setText(text)

    def update_style(self):
        base_color = "rgba(40, 44, 52, 220)" if not self.is_pressed else "rgba(97, 175, 239, 240)"
        border_color = "rgba(171, 178, 191, 100)" if not self.is_pressed else "rgba(97, 175, 239, 255)"
        text_color = "#ABB2BF" if not self.is_pressed else "#282C34"
        
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {base_color};
                border: 2px solid {border_color};
                border-radius: 10px;
                color: {text_color};
                font-family: 'Segoe UI', 'Inter', sans-serif;
                font-size: 13px;
                font-weight: bold;
                padding: 2px;
            }}
        """)

    def set_pressed(self, pressed):
        if self.is_pressed != pressed:
            self.is_pressed = pressed
            self.update_style()
            
    def set_layer(self, layer):
        if self.current_layer != layer:
            self.current_layer = layer
            self.update_text()

class TransparentGraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setStyleSheet("background: transparent; border: none;")
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # Enable anti-aliasing for smooth rotated rendering
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

class LayoutOverlay(QWidget):
    def __init__(self, json_path):
        super().__init__()
        self.json_path = json_path
        self.keys = {}  # Map position (0-19) to KeyWidget
        self.active_layers = set([0])
        
        self.init_ui()
        self.load_layout()
        
    def init_ui(self):
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.9)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 960, 290)
        
        # Draw background shapes mimicking the original web layout
        left_half = QGraphicsRectItem(0, 0, 450, 290)
        left_half.setBrush(QBrush(QColor(30, 41, 59, 120)))
        left_half.setPen(QPen(QColor(255, 255, 255, 20), 1))
        self.scene.addItem(left_half)

        right_half = QGraphicsRectItem(510, 0, 450, 290)
        right_half.setBrush(QBrush(QColor(30, 41, 59, 120)))
        right_half.setPen(QPen(QColor(255, 255, 255, 20), 1))
        self.scene.addItem(right_half)
        
        self.view = TransparentGraphicsView(self.scene, self)
        self.view.setFixedSize(960, 290)
        
        self.main_layout.addWidget(self.view)
        
        self.oldPos = self.pos()

    def load_layout(self):
        with open(self.json_path, 'r') as f:
            data = json.load(f)
            
        for key in data.get('keys', []):
            index = key['index']
            widget = KeyWidget(key)
            
            proxy = self.scene.addWidget(widget)
            
            if index in POSITIONS:
                pos = POSITIONS[index]
                # Rotate around center of the 64x64 keycap
                proxy.setTransformOriginPoint(32, 32) 
                proxy.setPos(pos['x'], pos['y'])
                proxy.setRotation(pos['r'])
            
            position = index - 1
            self.keys[position] = widget

    def on_key_pressed(self, position, state):
        if position in self.keys:
            self.keys[position].set_pressed(state)

    def on_layer_changed(self, layer, state):
        if state:
            self.active_layers.add(layer)
        else:
            self.active_layers.discard(layer)
            
        highest_layer = max(self.active_layers) if self.active_layers else 0
        
        for widget in self.keys.values():
            widget.set_layer(highest_layer)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()
