import json
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication, QGraphicsView, QGraphicsScene, QGraphicsProxyWidget, QGraphicsRectItem, QSizeGrip, QToolTip
from PySide6.QtGui import QColor, QPen, QBrush, QPainter, QCursor
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
    def __init__(self, key_data, layer_names=None, parent=None):
        super().__init__(parent)
        self.key_data = key_data
        self.layer_names = layer_names or {}
        self.index = key_data['index']
        self.is_pressed = False
        self.current_layer = 0
        self.active_layers = [0]
        
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(64, 64)
        self.update_style()
        self.update_text()
        
    def update_text(self):
        bindings = self.key_data.get('bindings', {})
        
        # Sort active layers descending to simulate a layer stack
        sorted_layers = sorted(list(self.active_layers), reverse=True)
        if 0 not in sorted_layers:
            sorted_layers.append(0)
            
        tap = ""
        hold = ""
        
        # Traverse the active layers stack downwards to find the first non-empty binding (handling &trans)
        for layer in sorted_layers:
            layer_bindings = bindings.get(str(layer), {})
            l_tap = layer_bindings.get('tap', '')
            l_hold = layer_bindings.get('hold', '')
            
            if l_tap != "":
                tap = l_tap
                hold = l_hold
                break
                
        # Ultimate fallback
        if tap == "":
            layer_bindings = bindings.get("0", {})
            tap = layer_bindings.get('tap', '')
            hold = layer_bindings.get('hold', '')
        
        # Clean up some ZMK specific codes for display
        def get_layer_name(layer_id_str):
            return self.layer_names.get(layer_id_str, f"L{layer_id_str}")

        if tap.startswith('&ht'):
            parts = tap.split(' ')
            tap = parts[-1] if len(parts) > 1 else tap
        elif tap.startswith('&lt'):
            parts = tap.split(' ')
            if len(parts) >= 3:
                hold = get_layer_name(parts[1])
                tap = parts[2]
            else:
                tap = parts[-1] if len(parts) > 1 else tap
        elif tap.startswith('&mtl'):
            parts = tap.split(' ')
            if len(parts) >= 3:
                # &mtl hold tap
                hold_val = get_layer_name(parts[1])
                tap_val = get_layer_name(parts[2])
                tap = tap_val
                hold = hold_val
            else:
                tap = parts[-1] if len(parts) > 1 else tap
        elif tap.startswith('&mo') or tap.startswith('&to') or tap.startswith('&tog') or tap.startswith('&sl'):
            parts = tap.split(' ')
            if len(parts) > 1:
                tap = get_layer_name(parts[1])
            else:
                tap = tap.replace('&mo', '').replace('&to', '').replace('&tog', '').replace('&sl', '').strip()
        elif tap.startswith('&kp') or tap.startswith('&mt'):
            tap = tap.replace('&kp', '').replace('&mt', '').strip()
            
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
        
        
        # Save full raw text for tooltip
        if l_hold:
            self.full_text = f"Tap: {l_tap}\nHold: {l_hold}"
        elif l_tap:
            self.full_text = f"{l_tap}"
        else:
            self.full_text = ""
            
        # ZMK Literature replacements
        zmk_names = {
            'NUMBER_1': '1',
            'NUMBER_2': '2',
            'NUMBER_3': '3',
            'NUMBER_4': '4',
            'NUMBER_5': '5',
            'NUMBER_6': '6',
            'NUMBER_7': '7',
            'NUMBER_8': '8',
            'NUMBER_9': '9',
            'NUMBER_0': '0',
            'N1': '1',
            'N2': '2',
            'N3': '3',
            'N4': '4',
            'N5': '5',
            'N6': '6',
            'N7': '7',
            'N8': '8',
            'N9': '9',
            'N0': '0',
            'KP_NUMBER_1': '1',
            'KP_NUMBER_2': '2',
            'KP_NUMBER_3': '3',
            'KP_NUMBER_4': '4',
            'KP_NUMBER_5': '5',
            'KP_NUMBER_6': '6',
            'KP_NUMBER_7': '7',
            'KP_NUMBER_8': '8',
            'KP_NUMBER_9': '9',
            'KP_NUMBER_0': '0',
            'MINUS': 'Keyboard - and _',
            'EQUAL': 'Keyboard = and +',
            'LBKT': 'Keyboard [ and {',
            'RBKT': 'Keyboard ] and }',
            'BSLH': 'Keyboard \\ and |',
            'SEMI': 'Keyboard ; and :',
            'SQT': 'Keyboard \' and "',
            'GRAVE': 'Keyboard ` and ~',
            'COMMA': 'Keyboard , and <',
            'DOT': 'Keyboard . and >',
            'FSLH': 'Keyboard / and ?'
        }
        
        for k, v in zmk_names.items():
            if k in text:
                text = text.replace(k, v)
            if hasattr(self, 'full_text') and k in self.full_text:
                self.full_text = self.full_text.replace(k, v)
                
        self.setText(text)

    def update_style(self):
        base_color = "rgba(40, 44, 52, 60)" if not self.is_pressed else "rgba(97, 175, 239, 140)"
        border_color = "rgba(171, 178, 191, 50)" if not self.is_pressed else "rgba(97, 175, 239, 200)"
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
            
    def set_layer(self, layer, active_layers=None):
        changed = False
        if self.current_layer != layer:
            self.current_layer = layer
            changed = True
        
        if active_layers is not None:
            new_active = list(active_layers)
            if self.active_layers != new_active:
                self.active_layers = new_active
                changed = True
                
        if changed:
            self.update_text()

    def enterEvent(self, event):
        super().enterEvent(event)
        if hasattr(self, 'full_text') and self.full_text:
            QToolTip.showText(QCursor.pos(), self.full_text, self)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        QToolTip.hideText()

class TransparentGraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setStyleSheet("background: transparent; border: none;")
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # Enable anti-aliasing for smooth rotated rendering
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

    def mousePressEvent(self, event):
        item = self.itemAt(event.position().toPoint())
        if isinstance(item, QGraphicsProxyWidget) and isinstance(item.widget(), KeyWidget):
            super().mousePressEvent(event)
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        item = self.itemAt(event.position().toPoint())
        if isinstance(item, QGraphicsProxyWidget) and isinstance(item.widget(), KeyWidget):
            super().mouseMoveEvent(event)
        else:
            event.ignore()

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
        self.setWindowOpacity(1.0)
        self.setStyleSheet("""
            LayoutOverlay {
                background-color: #0f172a;
            }
            QToolTip {
                background-color: #1e293b;
                color: #e2e8f0;
                border: 2px solid #3b82f6;
                border-radius: 6px;
                padding: 6px;
                font-size: 14px;
                font-family: 'Inter', sans-serif;
                font-weight: bold;
            }
        """)
        self.resize(960, 290)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 960, 290)
        
        # Draw background shapes mimicking the original web layout
        left_half = QGraphicsRectItem(0, 0, 450, 290)
        left_half.setBrush(QBrush(QColor(30, 41, 59, 255)))
        left_half.setPen(QPen(QColor(255, 255, 255, 20), 1))
        self.scene.addItem(left_half)

        right_half = QGraphicsRectItem(510, 0, 450, 290)
        right_half.setBrush(QBrush(QColor(30, 41, 59, 255)))
        right_half.setPen(QPen(QColor(255, 255, 255, 20), 1))
        self.scene.addItem(right_half)
        
        self.view = TransparentGraphicsView(self.scene, self)
        
        self.main_layout.addWidget(self.view)
        
        self.size_grip = QSizeGrip(self)
        self.size_grip.setFixedSize(20, 20)
        self.size_grip.setStyleSheet("background-color: rgba(255, 255, 255, 30); border-radius: 10px;")
        
        self.oldPos = self.pos()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.size_grip.move(self.width() - self.size_grip.width(), self.height() - self.size_grip.height())
        self.size_grip.raise_()

    def showEvent(self, event):
        super().showEvent(event)
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def load_layout(self):
        with open(self.json_path, 'r') as f:
            data = json.load(f)
            
        layer_names = {}
        for layer in data.get('layers', []):
            layer_names[str(layer.get('id', ''))] = layer.get('name', '')
            
        for key in data.get('keys', []):
            index = key['index']
            widget = KeyWidget(key, layer_names=layer_names)
            
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
        print(f"[OVERLAY] Layer changed signal received: layer={layer}, state={state}")
        if state:
            self.active_layers.add(layer)
        else:
            self.active_layers.discard(layer)
            
        print(f"[OVERLAY] Active layers: {self.active_layers}")
        highest_layer = max(self.active_layers) if self.active_layers else 0
        
        for widget in self.keys.values():
            widget.set_layer(highest_layer, self.active_layers)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPosition().toPoint()
        elif event.button() == Qt.RightButton:
            QApplication.quit()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta != 0:
            step = 0.05
            new_opacity = self.windowOpacity() + (step if delta > 0 else -step)
            # Limit transparency between 10% and 100%
            new_opacity = max(0.1, min(1.0, new_opacity))
            self.setWindowOpacity(new_opacity)
