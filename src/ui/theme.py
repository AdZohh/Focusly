# src/ui/theme.py
# Gestor simple de temas CSS para Focusly (PySide6)

# --- Colores base ---
DARK_BG = "#0b0b0f"
DARK_CARD = "#160f29"
TEXT = "#E6E6F0"
MORADO1 = "#6D28D9"
MORADO2 = "#8B5CF6"
ACCENT = "#7C3AED"
MUTED = "#9aa0c7"
BORDER = "rgba(124,58,237,0.12)"

LIGHT_BG = "#f7f7fb"
LIGHT_CARD = "#ffffff"
DARK_TEXT = "#160f29"
LIGHT_BORDER = "rgba(99,102,241,0.08)"


# ======================================================
# DARK THEME (CORREGIDO SIN DUPLICADOS)
# ======================================================

DARK_THEME = f"""
QMainWindow, QWidget {{
  background: {DARK_BG};
  color: {TEXT};
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
}}

QLabel {{
  background: transparent;
  border: none;
}}

QWidget#card {{
  background: #160f29;
  border-radius: 14px;
  border: 1px solid rgba(124,58,237,0.25);
  padding: 12px;
}}

QWidget#timer_card {{
  background: #160f29;
  border-radius: 14px;
  border: 2px solid rgba(124,58,237,0.95);
  padding: 18px;
  min-width: 340px;
}}

QListWidget {{
  background: #160f29;
  border-radius: 10px;
  padding: 6px;
  border: 1px solid rgba(124,58,237,0.15);
  color: {TEXT};
}}
QListWidget::item {{
  padding: 8px 10px;
  border-radius: 6px;
  margin: 2px;
  background: rgba(255,255,255,0.03);
}}
QListWidget::item:selected {{
  background: rgba(124,58,237,0.3);
  color: {TEXT};
}}
QListWidget::item:hover {{
  background: rgba(124,58,237,0.15);
}}

/* === BOTONES IGUAL QUE LIGHT THEME === */
QPushButton#primary {{
  background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
    stop:0 {MORADO1}, stop:1 {MORADO2});
  color: white;
  border-radius: 10px;
  padding: 8px 14px;
  border: none;
}}

QPushButton#secondary {{
  background: transparent;
  color: {TEXT};
  border-radius: 8px;
  padding: 6px 10px;
  border: 1px solid rgba(124,58,237,0.10);
}}

/* ===== WIDGETS DE MÉTRICAS ===== */
QWidget#metric_card {{
    background: #160f29;
    border-radius: 10px;
    padding: 15px;
    border: 1px solid rgba(124,58,237,0.4);
}}

QLabel#metric_label {{
    font-size: 12px; 
    color: white;
    font-weight: bold;
}}

QLabel#metric_value {{
    font-size: 28px; 
    font-weight: bold; 
    color: #8b5cf6;
}}

/* ===== DETALLES DE SESIÓN ===== */
QWidget#session_details_card {{
    background: #160f29;
    border-radius: 10px;
    padding: 15px;
    border: 1px solid rgba(124,58,237,0.4);
}}

QLabel#session_details_label {{
    font-size: 14px; 
    color: white;
    font-weight: bold;
}}

/* ===== PÁGINAS PRONTO ===== */
QWidget#soon_container {{
    background: #160f29;
    border-radius: 14px;
    border: 2px solid rgba(124,58,237,0.4);
    padding: 60px;
    margin: 20px;
}}

QLabel#soon_label {{
    font-size: 48px;
    font-weight: bold;
    color: rgba(124,58,237,0.7);
    background: transparent;
}}

/* SIDEBAR (Dashboard, Sesiones, etc) */
QListWidget {{
  background: #160f29;
  border-radius: 10px;
  padding: 6px;
  border: 1px solid rgba(124,58,237,0.15);
  color: {TEXT};
}}
QListWidget::item {{
  padding: 8px 10px;
  border-radius: 6px;
  margin: 2px;
}}
QListWidget::item:selected {{
  background: rgba(124,58,237,0.3);
  color: {TEXT};
}}

QProgressBar {{
  border-radius: 10px;
  background: rgba(255,255,255,0.02);
  height: 12px;
}}
QProgressBar::chunk {{
  background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #EC4899, stop:1 #8B5CF6);
  border-radius: 10px;
}}

QSlider::groove:horizontal {{
  border-radius: 6px;
  height: 10px;
  background: rgba(255,255,255,0.03);
}}
QSlider::sub-page:horizontal {{
  background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {MORADO1}, stop:1 {MORADO2});
  border-radius: 6px;
}}
QSlider::handle:horizontal {{
  background: {ACCENT};
  width: 16px;
  margin: -3px 0;
  border-radius: 8px;
  border: 2px solid rgba(255,255,255,0.06);
}}

QComboBox {{
  background: #0f1724;
  border-radius: 8px;
  padding: 6px;
  color: {TEXT};
  border: 1px solid rgba(124,58,237,0.06);
}}
QComboBox::drop-down {{
  width: 28px;
  border-left: 1px solid rgba(255,255,255,0.02);
}}

QLabel#muted {{
  color: {MUTED};
  font-size: 12px;
}}

QToolButton#theme_toggle {{
  background: rgba(124,58,237,0.1);
  border-radius: 8px;
  border: 1px solid rgba(124,58,237,0.2);
}}
QToolButton#theme_toggle:hover {{
  background: rgba(124,58,237,0.2);
}}

QLabel#header_icon {{
  background: transparent;
  border: none;
}}
"""


# ======================================================
# LIGHT THEME (CORREGIDO SIN DUPLICADOS)
# ======================================================

LIGHT_THEME = f"""
/* === SOLO TRANSPARENTE EN LABELS === */
QLabel {{
    background: transparent !important;
    border: none !important;
}}

* {{
    background: transparent;
}}

QMainWindow, QWidget {{
  background: {LIGHT_BG};
  color: {DARK_TEXT};
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
}}

QLabel#header_icon {{
  background: transparent;
  border: none;
}}

QWidget#card {{
  background: {LIGHT_CARD};
  border-radius: 14px;
  border: 1px solid {LIGHT_BORDER};
  padding: 12px;
}}

QWidget#timer_card {{
  background: transparent;
  border-radius: 14px;
  border: 2px solid rgba(124,58,237,0.95);
  padding: 18px;
  min-width: 340px;
}}

QLabel#title {{
  font-size: 26px;
  font-weight: 700;
  color: {DARK_TEXT};
}}

QPushButton#primary {{
  background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
    stop:0 {MORADO1}, stop:1 {MORADO2});
  color: white;
  border-radius: 10px;
  padding: 8px 14px;
  border: none;
}}

QPushButton#secondary {{
  background: transparent;
  color: {DARK_TEXT};
  border-radius: 8px;
  padding: 6px 10px;
  border: 1px solid rgba(0,0,0,0.06);
}}

QListWidget {{
  background: {LIGHT_CARD};
  border-radius: 10px;
  padding: 6px;
  border: 1px solid rgba(0,0,0,0.04);
  color: {DARK_TEXT};
}}
QListWidget::item {{
  padding: 6px 8px;
  border-radius: 6px;
  margin: 2px;
  background: rgba(0,0,0,0.02);
}}
QListWidget::item:selected {{
  background: rgba(124,58,237,0.15);
  color: {DARK_TEXT};
}}
QListWidget::item:hover {{
  background: rgba(124,58,237,0.08);
}}

/* ===== WIDGETS DE MÉTRICAS ===== */
QWidget#metric_card {{
    background: white;
    border-radius: 10px;
    padding: 15px;
    border: 1px solid rgba(124,58,237,0.4);
}}

QLabel#metric_label {{
    font-size: 12px; 
    color: black;
    font-weight: bold;
}}

QLabel#metric_value {{
    font-size: 28px; 
    font-weight: bold; 
    color: #8b5cf6;
}}

/* ===== DETALLES DE SESIÓN ===== */
QWidget#session_details_card {{
    background: white;
    border-radius: 10px;
    padding: 15px;
    border: 1px solid rgba(124,58,237,0.4);
}}

QLabel#session_details_label {{
    font-size: 14px; 
    color: black;
    font-weight: bold;
}}

/* ===== PÁGINAS PRONTO ===== */
QWidget#soon_container {{
    background: white;
    border-radius: 14px;
    border: 2px solid rgba(124,58,237,0.4);
    padding: 60px;
    margin: 20px;
}}

QLabel#soon_label {{
    font-size: 48px;
    font-weight: bold;
    color: rgba(124,58,237,0.7);
    background: transparent;
}}

/* LIST WIDGET */
QListWidget {{
  background: {LIGHT_CARD};
  border-radius: 10px;
  padding: 6px;
  border: 1px solid rgba(0,0,0,0.04);
  color: {DARK_TEXT};
}}
QListWidget::item {{
  padding: 6px 8px;
  border-radius: 6px;
  margin: 2px;
}}
QListWidget::item:selected {{
  background: rgba(124,58,237,0.15);
  color: {DARK_TEXT};
}}

QProgressBar {{
  border-radius: 10px;
  background: rgba(0,0,0,0.03);
  height: 12px;
}}
QProgressBar::chunk {{
  background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #EC4899, stop:1 #8B5CF6);
  border-radius: 10px;
}}

QSlider::groove:horizontal {{
  border-radius: 6px;
  height: 10px;
  background: rgba(0,0,0,0.04);
}}
QSlider::sub-page:horizontal {{
  background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {MORADO1}, stop:1 {MORADO2});
  border-radius: 6px;
}}
QSlider::handle:horizontal {{
  background: {ACCENT};
  width: 16px;
  margin: -3px 0;
  border-radius: 8px;
  border: 2px solid rgba(0,0,0,0.06);
}}

QComboBox {{
  background: #ffffff;
  border-radius: 8px;
  padding: 6px;
  color: {DARK_TEXT};
  border: 1px solid rgba(0,0,0,0.04);
}}

QLabel#muted {{
  color: #6b7280;
  font-size: 12px;
}}

QToolButton#theme_toggle {{
  background: rgba(124,58,237,0.1);
  border-radius: 8px;
  border: 1px solid rgba(124,58,237,0.2);
}}
QToolButton#theme_toggle:hover {{
  background: rgba(124,58,237,0.2);
}}
"""


# ======================================================
# Theme Manager
# ======================================================

class ThemeManager:
    def __init__(self, app):
        self.app = app
        self.dark = True
        self.pattern_bg = None
        self.circle_score = None
        self.metric_widgets = []  #Lista para trackear widgets de métricas

    def add_metric_widget(self, widget_func):
        """Añadir función de actualización de métricas"""
        self.metric_widgets.append(widget_func)

    def update_metric_widgets(self):
        """Actualizar todos los widgets de métricas"""
        for widget_func in self.metric_widgets:
            widget_func()

    def apply_dark(self):
        self.app.setStyleSheet(DARK_THEME)
        self.dark = True
        if self.pattern_bg:
            self.pattern_bg.set_dark_mode(True)
        if self.circle_score:
            self.circle_score.set_dark_mode(True)
        self.update_metric_widgets()  # ⭐⭐ ACTUALIZAR MÉTRICAS

    def apply_light(self):
        self.app.setStyleSheet(LIGHT_THEME)
        self.dark = False
        if self.pattern_bg:
            self.pattern_bg.set_dark_mode(False)
        if self.circle_score:
            self.circle_score.set_dark_mode(False)
        self.update_metric_widgets()  # ⭐⭐ ACTUALIZAR MÉTRICAS

    def set_pattern_background(self, pattern_bg):
        self.pattern_bg = pattern_bg

    def set_circle_score(self, circle_score):
        self.circle_score = circle_score

    def apply_dark(self):
        self.app.setStyleSheet(DARK_THEME)
        self.dark = True
        if self.pattern_bg:
            self.pattern_bg.set_dark_mode(True)
        if self.circle_score:
            self.circle_score.set_dark_mode(True)

    def apply_light(self):
        self.app.setStyleSheet(LIGHT_THEME)
        self.dark = False
        if self.pattern_bg:
            self.pattern_bg.set_dark_mode(False)
        if self.circle_score:
            self.circle_score.set_dark_mode(False)

    def toggle(self):
        if self.dark:
            self.apply_light()
        else:
            self.apply_dark()

