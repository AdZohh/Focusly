# src/core/pomodoro.py
from PySide6.QtCore import QObject, Signal, QTimer
import time  

class Pomodoro(QObject):
    """
    Control simple de Pomodoro usando QTimer.
    Signals:
      tick(minutes, seconds)
      finished()
      started()
      paused()
    """
    tick = Signal(int, int)
    finished = Signal()
    started = Signal()
    paused = Signal()

    def __init__(self, minutes=25, break_minutes=5):
        super().__init__()
        self.default_minutes = minutes
        self.break_minutes = break_minutes
        self.remaining = minutes * 60
        self.total_seconds = minutes * 60 
        self._running = False
        self.start_time = None 
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._on_tick)

    def start(self):
        self._running = True
        self.start_time = time.time()  
        self.timer.start()
        self.started.emit()

    def pause(self):
        if self._running:
            self.timer.stop()
            self._running = False
            self.paused.emit()

    def reset(self):
        self.timer.stop()
        self._running = False
        self.remaining = self.default_minutes * 60
        self.total_seconds = self.default_minutes * 60  
        self.start_time = None  
        self.tick.emit(self.default_minutes, 0)

    def _on_tick(self):
        if self.remaining <= 0:
            self.timer.stop()
            self._running = False
            self.finished.emit()
            return
        self.remaining -= 1
        m, s = divmod(self.remaining, 60)
        self.tick.emit(m, s)

    def format_time(self):
        m, s = divmod(self.remaining, 60)
        return f"{m:02d}:{s:02d}"

    @property
    def is_running(self):
        """Indica si el pomodoro está corriendo"""
        return self._running

    @property
    def elapsed_seconds(self):
        """Tiempo transcurrido desde que empezó la sesión"""
        if self._running and self.start_time:
            return int(time.time() - self.start_time)
        return 0