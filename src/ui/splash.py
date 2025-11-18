# src/ui/splash.py
import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QApplication, QToolButton, QHBoxLayout
)
from PySide6.QtGui import QPixmap, QFont, Qt

# 🎨 Colores base
BG_DARK = "#07060a"       # fondo oscuro puro
BG_LIGHT = "#fbfbfd"
TEXT_DARK = "#EDF0FF"
TEXT_LIGHT = "#0f1724"
PURPLE1 = "#6D28D9"
PURPLE2 = "#8B5CF6"
MUTED = "#9aa0c7"


class SplashDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dark_mode = True  # tema inicial

        self.setWindowTitle("Focusly - Bienvenido")
        # un poco más alto para que se vea ligeramente rectangular (vertical)
        self.setFixedSize(520, 440)
        self.setWindowModality(Qt.ApplicationModal)

        # --- Layout principal ---
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 28, 30, 20)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # --- Icono central ---
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "icon.png"))
        if os.path.exists(icon_path):
            pix = QPixmap(icon_path).scaled(92, 92, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label = QLabel()
            icon_label.setPixmap(pix)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_label.setContentsMargins(0, 6, 0, 6)
            layout.addWidget(icon_label)
        else:
            v = QLabel("🎧")
            v.setFont(QFont("Segoe UI Emoji", 56))
            v.setAlignment(Qt.AlignmentFlag.AlignCenter)
            v.setContentsMargins(0, 6, 0, 6)
            layout.addWidget(v)

        # --- Título ---
        self.title = QLabel("Focusly")
        self.title.setFont(QFont("Montserrat", 34, QFont.Bold))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title)

        # --- Subtítulo ---
        self.subtitle = QLabel("Tu espacio para enfocarte al máximo")
        self.subtitle.setFont(QFont("Segoe UI", 12))
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.subtitle)

        layout.addStretch(1)

        # --- Botón "Iniciar" ---
        self.btn_start = QPushButton("Iniciar")
        self.btn_start.setFixedSize(180, 46)
        self.btn_start.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.btn_start, alignment=Qt.AlignmentFlag.AlignCenter)

        # --- Footer con texto + botón tema centrado ---
        footer_row = QHBoxLayout()
        footer_row.setContentsMargins(0, 4, 0, 0)
        footer_row.setSpacing(10)
        footer_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Etiqueta izquierda (fija para ayudar al centrado)
        self.footer_left = QLabel("")  # texto se setea en apply_theme
        self.footer_left.setFont(QFont("Segoe UI", 10))
        self.footer_left.setFixedWidth(140)
        self.footer_left.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        footer_row.addWidget(self.footer_left)

        # Botón del tema (centrado)
        self.theme_toggle = QToolButton()
        self.theme_toggle.setCheckable(True)
        self.theme_toggle.setFixedSize(36, 28)
        self.theme_toggle.setToolTip("Cambiar tema")
        self.theme_toggle.clicked.connect(self.toggle_theme)
        footer_row.addWidget(self.theme_toggle, alignment=Qt.AlignmentFlag.AlignCenter)

        # Etiqueta derecha (fija para ayudar al centrado)
        self.footer_right = QLabel("Acento morado")
        self.footer_right.setFont(QFont("Segoe UI", 10))
        self.footer_right.setFixedWidth(140)
        self.footer_right.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        footer_row.addWidget(self.footer_right)

        layout.addLayout(footer_row)

        # Conectar botón "Iniciar" → cerrar
        self.btn_start.clicked.connect(self.accept)

        # Aplicar tema inicial (ahora que widgets existen)
        self.apply_theme()

    # ---------------- TEMAS -----------------
    def apply_theme(self):
        """Aplica el tema actual (oscuro o claro) con estilos coherentes."""
        if self.dark_mode:
            self.setStyleSheet(f"""
                QDialog {{
                    background: {BG_DARK};
                    color: {TEXT_DARK};
                }}
                QLabel {{
                    color: {TEXT_DARK};
                }}
                QPushButton {{
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                        stop:0 {PURPLE1}, stop:1 {PURPLE2});
                    color: white;
                    border-radius: 10px;
                    font-weight: 600;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    opacity: 0.95;
                }}
                QToolButton {{
                    background: transparent;
                    border-radius: 6px;
                    color: {TEXT_DARK};
                    font-size: 16px;
                }}
                QToolButton:checked {{
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                        stop:0 {PURPLE1}, stop:1 {PURPLE2});
                    color: white;
                }}
            """)
            self.theme_toggle.setText("🌙")
            self.theme_toggle.setChecked(True)
            self.footer_left.setText("Modo oscuro")
        else:
            self.setStyleSheet(f"""
                QDialog {{
                    background: {BG_LIGHT};
                    color: {TEXT_LIGHT};
                }}
                QLabel {{
                    color: {TEXT_LIGHT};
                }}
                QPushButton {{
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                        stop:0 {PURPLE1}, stop:1 {PURPLE2});
                    color: white;
                    border-radius: 10px;
                    font-weight: 600;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    opacity: 0.95;
                }}
                QToolButton {{
                    background: transparent;
                    border-radius: 6px;
                    color: {TEXT_LIGHT};
                    font-size: 16px;
                }}
                QToolButton:checked {{
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                        stop:0 {PURPLE1}, stop:1 {PURPLE2});
                    color: white;
                }}
            """)
            self.theme_toggle.setText("☀️")
            self.theme_toggle.setChecked(False)
            self.footer_left.setText("Modo claro")

    def toggle_theme(self):
        """Alterna entre tema oscuro y claro."""
        self.dark_mode = not self.dark_mode
        self.apply_theme()




