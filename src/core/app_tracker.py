# src/core/app_tracker.py
from PySide6.QtCore import QThread, Signal
import time
import psutil

# Import Windows APIs if on Windows
try:
    import win32gui
    import win32process
except Exception:
    win32gui = None
    win32process = None

class AppTracker(QThread):
    """
    Hilo que emite la app/ventana activa cada segundo.
    Señal: active_changed(process_name, window_title)
    """
    active_changed = Signal(str, str)

    def __init__(self, poll_interval=1.0):
        super().__init__()
        self.poll_interval = poll_interval
        self._running = False
        self._last_process = None
        self._last_title = None

    def run(self):
        self._running = True
        while self._running:
            try:
                if win32gui:
                    hwnd = win32gui.GetForegroundWindow()
                    title = win32gui.GetWindowText(hwnd) if hwnd else ""
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    proc_name = None
                    try:
                        proc = psutil.Process(pid)
                        proc_name = proc.name()
                    except Exception:
                        proc_name = None
                    
                    current_proc = proc_name or ""
                    current_title = title or ""
                    
                    # ⭐⭐ SIEMPRE emitir, incluso si es la misma ventana ⭐⭐
                    self.active_changed.emit(current_proc, current_title)
                    self._last_process = current_proc
                    self._last_title = current_title
                    
                else:
                    # Fallback: emit nothing on non-windows for now
                    pass
            except Exception as e:
                print("AppTracker error:", e)
            time.sleep(self.poll_interval)

    def stop(self):
        self._running = False
        self.quit()
        self.wait()
