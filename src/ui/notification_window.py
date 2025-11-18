# src/ui/notification_window.py
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QIcon, QPixmap
import os

class NotificationWindow(QDialog):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        # ⭐⭐ QUITAR la transparencia ⭐⭐
        # self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(400, 120)
        
        # ⭐⭐ MEJORAR el estilo - más opaco y visible ⭐⭐
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f0f23, stop:1 #1a1a2e);
                border-radius: 15px;
                border: 2px solid #7c3aed;
            }
            QLabel {
                color: white;
                background: transparent;
                font-family: "Segoe UI", Arial;
            }
            QLabel#title {
                font-size: 16px;
                font-weight: bold;
                color: #a78bfa;
            }
            QLabel#message {
                font-size: 14px;
                padding: 8px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7c3aed, stop:1 #6d28d9);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8b5cf6, stop:1 #7c3aed);
            }
        """)
        
        self._setup_ui(message)
        self._setup_animation()
        
    def _setup_ui(self, message):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)
        
        # Header con icono y título
        header_layout = QHBoxLayout()
        
        # Icono
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "icon.png"))
        icon_label = QLabel()
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        else:
            icon_label.setText("🎯")
            icon_label.setStyleSheet("font-size: 20px;")
        icon_label.setFixedSize(24, 24)
        
        # Título
        title_label = QLabel("Focusly")
        title_label.setObjectName("title")
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Botón cerrar
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.clicked.connect(self.hide)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: #ef4444;
                color: white;
                border-radius: 12px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #dc2626;
            }
        """)
        header_layout.addWidget(self.close_btn)
        
        # Mensaje
        message_label = QLabel(message)
        message_label.setObjectName("message")
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignCenter)
        
        layout.addLayout(header_layout)
        layout.addWidget(message_label)
        
        self.setLayout(layout)
        
    def _setup_animation(self):
        # Animación de entrada
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Timer para auto-cerrar
        self.close_timer = QTimer()
        self.close_timer.setSingleShot(True)
        self.close_timer.timeout.connect(self._fade_out)
        
    def show_notification(self, duration=8000):
        # Posicionar en esquina inferior derecha
        screen_geo = self.screen().availableGeometry()
        x = screen_geo.width() - self.width() - 20
        y = screen_geo.height() - self.height() - 20
        self.move(x, y)
        
        self.show()
        self.animation.start()
        # PARÁMETRO 
        self.close_timer.start(duration)
        
    def _fade_out(self):
        self.animation.setDirection(QPropertyAnimation.Backward)
        self.animation.finished.connect(self.hide)
        self.animation.start()
        
    def hide(self):
        self.close_timer.stop()
        super().hide()