# src/core/notifier.py
from PySide6.QtCore import QObject, Signal, QUrl
from ui.notification_window import NotificationWindow 
from PySide6.QtMultimedia import QSoundEffect
import os

class Notifier(QObject):
    notify_signal = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.notification_windows = []  # Para mantener referencia
        self.sound_effect = QSoundEffect()
        sound_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "..", "assets", "notification.wav"
        ))
        
        if os.path.exists(sound_path):
            self.sound_effect.setSource(QUrl.fromLocalFile(sound_path))
            self.sound_effect.setVolume(0.7)  # Volumen al 70%
        else:
            print("[Notifier] Sonido de notificación no encontrado")

    def notify(self, message, kind="info"):
        print(f"[Notifier] {kind}: {message}")
        self.notify_signal.emit(kind, message)
        
        #
        if kind == "score_alert":
            self._play_notification_sound()
        
        # Mostrar notificación visual
        self._show_visual_notification(message, kind)

    def _play_notification_sound(self):
        """Reproduce sonido de notificación"""
        try:
            if self.sound_effect.source().isValid():
                self.sound_effect.play()
        except Exception as e:
            print(f"[Notifier] Error reproduciendo sonido: {e}")

    def _show_visual_notification(self, message, kind):
        """Muestra notificación visual"""
        try:
            # 
            if kind == "score_alert":
                duration = 8000   # 8 segundos para score
            else:
                duration = 3000   # 3 segundos para distracciones
            
            # Todo lo demás igual
            notification = NotificationWindow(message)
            self.notification_windows.append(notification)
            
            notification.destroyed.connect(
                lambda: self.notification_windows.remove(notification) 
                if notification in self.notification_windows else None
            )
            
            notification.show_notification(duration)
            
        except Exception as e:
            print(f"[Notifier] Error mostrando notificación visual: {e}")