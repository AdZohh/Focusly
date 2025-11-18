# src/ui/run_app.py
import sys
import os

# Rutas para que funcione en .exe Y desarrollo
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

from PySide6.QtWidgets import QApplication

# IMPORT CORREGIDO - funciona en .exe y desarrollo
try:
    # Para .exe
    from splash import SplashDialog
    from main_window import FocuslyMain
except ImportError:
    # Para desarrollo  
    from ui.splash import SplashDialog
    from ui.main_window import FocuslyMain

if __name__ == "__main__":
    app = QApplication(sys.argv)

    splash = SplashDialog()
    result = splash.exec()

    if result == 1:
        window = FocuslyMain()
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)