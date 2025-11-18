# src/ui/main_window.py
import sys
import os
import time
import re
import datetime
# permitir imports relativos desde src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ui.theme import ThemeManager

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QStackedWidget, QSlider, QComboBox,
    QToolButton, QGraphicsDropShadowEffect, QSizePolicy
)
from PySide6.QtCore import Qt, Slot, QPointF, QTimer
from PySide6.QtGui import QIcon, QPixmap, QColor, QPainter, QPolygonF, QBrush, QFont, QPainterPath, QPen
from PySide6.QtCharts import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis

# Imports de los módulos core (esqueletos)
from core.app_tracker import AppTracker
from core.pomodoro import Pomodoro
from core.audio_manager import AudioManager
from core.focus_scorer import FocusScorer
from core.notifier import Notifier
from data import database

# imports StatsPage y SessionsPage:
from ui.sessions_page import SessionsPage
from ui.stats_page import StatsPage


# Nuevo helper: Background con patrón (dibujado por QPainter)

class PatternBackground(QWidget):
    """Widget contenedor que dibuja líneas asimétricas en el fondo."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dark_mode = True

    def set_dark_mode(self, is_dark):
        self.dark_mode = is_dark
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Fondo base que cambia con el tema
        if self.dark_mode:
            p.fillRect(self.rect(), QColor("#0b0b0f"))
        else:
            p.fillRect(self.rect(), QColor("#f7f7fb"))

        w = self.width()
        h = self.height()

            # Colores del patrón según el tema
        
        if self.dark_mode:
            line_color = QColor(124, 58, 237, 15)    # Morado muy sutil
            shape_color = QColor(139, 92, 246, 8)    # Figuras más sutiles
        else:
            line_color = QColor(124, 58, 237, 8)     # Morado claro muy sutil
            shape_color = QColor(139, 92, 246, 5)    # Figuras casi transparentes

        p.setPen(QPen(line_color, 1.5))

        # Líneas diagonales asimétricas
        p.drawLine(QPointF(w*0.1, h*0.1), QPointF(w*0.3, h*0.3))
        p.drawLine(QPointF(w*0.8, h*0.2), QPointF(w*0.9, h*0.4))
        p.drawLine(QPointF(w*0.2, h*0.7), QPointF(w*0.4, h*0.9))
        p.drawLine(QPointF(w*0.7, h*0.6), QPointF(w*0.85, h*0.8))
        
        # Líneas curvas suaves
        path = QPainterPath()
        path.moveTo(w*0.6, h*0.1)
        path.quadTo(w*0.8, h*0.2, w*0.7, h*0.4)
        p.drawPath(path)
        
        path2 = QPainterPath()
        path2.moveTo(w*0.3, h*0.5)
        path2.quadTo(w*0.1, h*0.7, w*0.4, h*0.9)
        p.drawPath(path2)

        # Figuras geométricas irregulares (sin relleno, solo bordes)
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(shape_color, 1))
        
        # Triángulo irregular
        triangle = QPolygonF([
            QPointF(w*0.15, h*0.15),
            QPointF(w*0.25, h*0.08),
            QPointF(w*0.2, h*0.25)
        ])
        p.drawPolygon(triangle)
        
        # Pentágono irregular
        pentagon = QPolygonF([
            QPointF(w*0.75, h*0.15),
            QPointF(w*0.85, h*0.2),
            QPointF(w*0.8, h*0.35),
            QPointF(w*0.7, h*0.3),
            QPointF(w*0.72, h*0.2)
        ])
        p.drawPolygon(pentagon)
        
        # Líneas horizontales/verticales sutiles
        p.setPen(QPen(line_color, 0.8))
        for i in range(3):
            y = h * (0.2 + i * 0.15)
            p.drawLine(QPointF(w*0.05, y), QPointF(w*0.25, y))
            
        for i in range(2):
            x = w * (0.7 + i * 0.15)
            p.drawLine(QPointF(x, h*0.6), QPointF(x, h*0.8))

        p.end()


# Score circular: CircleScore widget

class CircleScore(QWidget):
    def __init__(self, parent=None, size=120):
        super().__init__(parent)
        self._value = 100
        self._size = size
        self.dark_mode = True
        self.setFixedSize(size, size)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def set_dark_mode(self, is_dark):
        self.dark_mode = is_dark
        self.update()

    def setValue(self, v:int):
        self._value = max(0, min(100, int(v)))
        self.update()

    def paintEvent(self, event):
        r = min(self.width(), self.height())
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # fondo circular que cambia con el tema
        center = self.rect().center()
        radius = r//2 - 2
        if self.dark_mode:
            bg_color = QColor(16, 11, 20)  # oscuro interior
            text_color = QColor(230, 230, 240)
        else:
            bg_color = QColor(245, 245, 250)  # claro interior
            text_color = QColor(60, 60, 80)
        
        p.setBrush(QBrush(bg_color))
        p.setPen(QColor(0,0,0,0))
        p.drawEllipse(center, radius, radius)

        # arco (progresivo) en morado
        pen = p.pen()
        pen.setWidth(8)
        pen.setColor(QColor(124, 58, 237, 220))  # morado opaco
        p.setPen(pen)

        # draw arc proportional to value (start at -90deg)
        import math
        start_angle = -90
        span = int(360 * (self._value/100.0))
        p.drawArc(self.rect().adjusted(8,8,-8,-8), (start_angle)*16, -span*16)

        # Texto central - ASEGURARSE QUE NO TENGA FONDO
        p.setPen(text_color)
        font = QFont("Segoe UI", 11, QFont.Bold)
        p.setFont(font)
        txt = f"{self._value}%"
        metrics = p.fontMetrics()
        tw = metrics.horizontalAdvance(txt)
        th = metrics.height()
        
        # Dibujar texto SIN fondo
        p.setBackgroundMode(Qt.TransparentMode) 
        p.drawText(center.x() - tw/2, center.y() + th/4, txt)

        p.end()


# MAIN
class FocuslyMain(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Focusly")
        self.setGeometry(300, 150, 1000, 620)
        
        # Inicializar DB PRIMERO
        database.init_db()

        # Theme manager ANTES de construir UI
        self.theme_manager = ThemeManager(QApplication.instance())
        self.theme_manager.apply_dark()
        
        # Inicializar componentes core ANTES de UI (pero con valores por defecto)
        self.pomodoro = Pomodoro()
        self.audio = AudioManager()
        self._audio_paused = False
        self.tracker = AppTracker(poll_interval=2.0)
        self.scorer = FocusScorer()
        self.notifier = Notifier()

        self.app_history = {}  # { (proc, title): accumulated_seconds }
        self.last_app_key = None

        self.session_start_time = None

        # Conectar notificaciones de distracciones Y score
        def on_distraction_detected(proc, title, seconds):
            if proc == "score_alert":
                # Es una notificación de score, no de distracción específica
                self.notifier.notify(title, kind="score_alert")  # title contiene el mensaje
            else:
                # Notificación de distracción normal
                distraction_minutes = seconds / 60
                message = f"Llevas {distraction_minutes:.1f} minutos en {proc}\n¡Vuelve a enfocarte!"
                self.notifier.notify(message, kind="distraction")

        self.scorer.distraction_detected.connect(on_distraction_detected)

        # Estado para tracking
        self._tracker_running = False
        self._last_active_proc = None
        self._last_active_title = None
        self._last_active_ts = None
        
        # Configurar scorer
        self.scorer.distractor_threshold_seconds = 60
        self.scorer.window_seconds = 25 * 60
        self.timer_duration = 25 * 60

        print(f"[INIT] Scorer iniciado - Último notificado: {self.scorer.last_notified_score}%")

        # Construir UI DESPUÉS de tener todos los componentes
        self._build_ui()
        
        self.theme_manager.set_pattern_background(self.centralWidget())  # central es el PatternBackground
        self.theme_manager.set_circle_score(self.circle_score)
        
        # Restaurar icono
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "icon.png"))
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Conectar signals DESPUÉS de construir UI
        self.tracker.active_changed.connect(self.on_active_changed)
        self.pomodoro.tick.connect(self.on_tick)
        self.pomodoro.finished.connect(self.on_pomodoro_finished)
        self.notifier.notify_signal.connect(self.on_notify)
        
        # Forzar una actualización inicial
        self.label_timer.setText(self.pomodoro.format_time())

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.force_score_update)
        self.update_timer.start(5000)  # Actualizar cada 5 segundos

    # Nuevo método:
    def force_score_update(self):
        """Forzar actualización del score cada X segundos"""
        try:
            print(f"[DEBUG] Force update - Historial tiene {len(self.scorer.history)} eventos")
            score = self.get_progressive_score()
            print(f"[DEBUG] Score actual: {score}%")
            
            if hasattr(self, "label_score"):
                self.label_score.setText(f"Score: {score}")
            if hasattr(self, "circle_score"):
                self.circle_score.setValue(score)
        except Exception as e:
            print("[DEBUG] Error actualizando score:", e)


    def get_progressive_score(self):
        """Score por puntos - cada minuto de distracción quita puntos fijos"""
        try:
            target_minutes = self.input_minutes.value()
            
            # Calcular tiempo transcurrido
            if hasattr(self, 'session_start_time') and self.session_start_time:
                elapsed = (datetime.datetime.now() - self.session_start_time).total_seconds()
            else:
                elapsed = getattr(self.pomodoro, 'elapsed_seconds', 0)
            
            if elapsed < 10:
                return 100
            
            # Calcular tiempo en distracciones (en minutos)
            distracting_time = 0
            for (proc, title), seconds in self.app_history.items():
                if self.scorer._is_distractor_by_name(proc, title):
                    distracting_time += seconds
            
            distracting_minutes = distracting_time / 60
            
            print(f"[SCORE PUNTOS] Objetivo: {target_minutes}min | Distracción: {distracting_minutes:.1f}min")
            
            # ⭐⭐ SISTEMA DE PUNTOS SUPER SIMPLE ⭐⭐
            # Cada minuto de distracción quita puntos según la duración objetivo:
            points_per_distraction_minute = 100 / target_minutes
            
            score = max(0, 100 - int(distracting_minutes * points_per_distraction_minute))
            
            print(f"[SCORE PUNTOS] Puntos/min: {points_per_distraction_minute:.1f} | Score: {score}%")
            return score
            
        except Exception as e:
            print("[DEBUG] Error calculando score:", e)
            return 100

    def _on_category_changed(self, category):
        """Método reutilizable para rellenar pistas desde fuera."""
        try:
            # reutiliza la lógica del bloque anterior
            tracks = []
            if hasattr(self.audio, "get_tracks"):
                tracks = list(self.audio.get_tracks(category))
            elif hasattr(self.audio, "presets") and category in self.audio.presets:
                val = self.audio.presets[category]
                if isinstance(val, (list, tuple)):
                    tracks = list(val)
                else:
                    tracks = [val]
            else:
                folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "sounds", category))
                if os.path.isdir(folder):
                    for f in sorted(os.listdir(folder)):
                        if f.lower().endswith((".wav", ".mp3", ".ogg")):
                            tracks.append(f)
            self.track_selector.clear()
            for t in tracks:
                label = os.path.splitext(t)[0].replace("_", " ").title()
                self.track_selector.addItem(label, t)
            if self.track_selector.count() > 0:
                self.track_selector.setCurrentIndex(0)
        except Exception as e:
            print("[Audio] _on_category_changed error:", e)

    def _on_track_changed(self, track):
        """Reproduce un track dado (track = filename)."""
        try:
            if not track:
                return
            cat = self.category_selector.currentText() if hasattr(self, "category_selector") else None
            if hasattr(self.audio, "play_track"):
                self.audio.play_track(cat, track)
            elif hasattr(self.audio, "play_preset"):
                # intentar usar play_preset con la categoría
                try:
                    self.audio.play_preset(cat)
                except Exception:
                    # fallback: play path si existe
                    if hasattr(self.audio, "play"):
                        p = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "sounds", cat or "", track))
                        if os.path.exists(p):
                            self.audio.play(p)
            elif hasattr(self.audio, "play"):
                p = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "sounds", cat or "", track))
                if os.path.exists(p):
                    self.audio.play(p)
        except Exception as e:
            print("[Audio] _on_track_changed error:", e)

    def _build_ui(self):
        print("[DEBUG] Iniciando _build_ui...")
        # --- central con pattern background ---
        central = PatternBackground()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(18, 18, 18, 18)
        central.setLayout(main_layout)
        self.setCentralWidget(central)

        # ---------- LEFT PANEL: header pequeño + sidebar ----------
        left_panel = QWidget()
        left_panel.setFixedWidth(220)
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(8, 8, 8, 8)
        left_layout.setSpacing(8)
        left_panel.setLayout(left_layout)

        # --- HEADER ROW: icon (left) + spacer + theme toggle (right) ---
        header_row = QHBoxLayout()
        header_row.setContentsMargins(6, 6, 6, 6)
        header_row.setSpacing(6)

        # ---------- Stack area ----------
        self.stack = QStackedWidget()

        # mini logo (si existe) — lo dejamos con objectName para poder estilizarlo
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "icon.png"))
        mini = QLabel()
        if os.path.exists(icon_path):
            pix = QPixmap(icon_path).scaled(26, 26, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            mini.setPixmap(pix)
        else:
            mini.setText("🎧")
        mini.setFixedSize(28, 28)
        mini.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mini.setObjectName("header_icon")   # <- para CSS
        header_row.addWidget(mini, alignment=Qt.AlignmentFlag.AlignLeft)

        header_row.addStretch(1)

        # theme toggle button (🌙 / ☀️)
        self.theme_toggle = QToolButton()
        self.theme_toggle.setText("🌙")
        self.theme_toggle.setCheckable(True)
        self.theme_toggle.setFixedSize(36, 28)
        self.theme_toggle.clicked.connect(self.on_toggle_theme)
        self.theme_toggle.setObjectName("theme_toggle")  # <- para CSS
        header_row.addWidget(self.theme_toggle, alignment=Qt.AlignmentFlag.AlignRight)

        left_layout.addLayout(header_row)


        # sidebar (lista de navegación)
        self.sidebar = QListWidget()
        self.sidebar.addItems(["Dashboard", "Sesiones", "Estadísticas", "Presets", "Configuración"])
        self.sidebar.setFixedWidth(200)
        self.sidebar.currentRowChanged.connect(self.on_nav_changed)
        left_layout.addWidget(self.sidebar)

        main_layout.addWidget(left_panel)

        self.sidebar.setCurrentRow(0)

        left_layout.addWidget(self.sidebar)

        # añadir stack al main layout
        main_layout.addWidget(self.stack, 1)

        # ---------- Dashboard page ----------
        self.page_dashboard = QWidget()
        dash_layout = QHBoxLayout()
        dash_layout.setSpacing(18)
        self.page_dashboard.setLayout(dash_layout)
        self.dash_layout = dash_layout

        # ----------------- CENTER: Timer card (centrado) -----------------
        # (idempotente: elimina instancias previas antes de crear nuevas para evitar duplicados)
        # quitar referencias previas si existen (evita widgets huérfanos que ocupan todo)
        try:
            if hasattr(self, "timer_card") and self.timer_card is not None:
                prev = self.timer_card
                prev.setParent(None)
        except Exception:
            pass

        try:
            if hasattr(self, "center_container") and self.center_container is not None:
                prevc = self.center_container
                prevc.setParent(None)
        except Exception:
            pass

        # crear timer_card
        timer_card = QWidget()
        timer_layout = QVBoxLayout(timer_card)
        timer_layout.setContentsMargins(18, 18, 18, 18)
        timer_layout.setSpacing(12)
        timer_card.setLayout(timer_layout)
        timer_card.setObjectName("timer_card")
        # evitar que se estire a pantalla completa (esto podía causar el "negro")
        timer_card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        timer_card.setMaximumWidth(520)   # evita llenar todo el ancho
        timer_card.setMinimumWidth(340)

        self.timer_card = timer_card  # referencia para otros métodos

        # Timer grande (reusar si ya existe)
        if not hasattr(self, "label_timer"):
            self.label_timer = QLabel("25:00")  # ← Valor por defecto
            # La actualización real se hará después en el __init__
            self.label_timer.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.label_timer.setStyleSheet("font-size: 56px; font-weight: 700;")
            timer_layout.addWidget(self.label_timer, alignment=Qt.AlignmentFlag.AlignCenter)

        # Botones Start / Pause / Reset (centrados, estilo ya aplicado por objectName)
        controls_row = QHBoxLayout()
        controls_row.setSpacing(10)

        if not hasattr(self, "btn_start"):
            self.btn_start = QPushButton("Start")
            self.btn_start.setObjectName("primary")
            self.btn_start.setFixedHeight(38)
            self.btn_start.clicked.connect(self.on_start)
        if not hasattr(self, "btn_pause"):
            self.btn_pause = QPushButton("Pause")
            self.btn_pause.setObjectName("primary")
            self.btn_pause.setFixedHeight(38)
            self.btn_pause.clicked.connect(self.on_pause)
        if not hasattr(self, "btn_reset"):
            self.btn_reset = QPushButton("Reset")
            self.btn_reset.setObjectName("primary")
            self.btn_reset.setFixedHeight(38)
            self.btn_reset.clicked.connect(self.on_reset)

        # centramos botones con stretch para que no peguen a los bordes
        controls_row.addStretch(1)
        controls_row.addWidget(self.btn_start)
        controls_row.addWidget(self.btn_pause)
        controls_row.addWidget(self.btn_reset)
        controls_row.addStretch(1)
        timer_layout.addLayout(controls_row)

        # === Input editable del temporizador (SpinBox + Set) ===
        from PySide6.QtWidgets import QSpinBox
        if not hasattr(self, "input_minutes"):
            self.input_minutes = QSpinBox()
            self.input_minutes.setRange(1, 180)
            self.input_minutes.setValue(25)
            self.input_minutes.setSuffix(" min")
            self.input_minutes.setFixedWidth(120)

        if not hasattr(self, "btn_set_timer"):
            self.btn_set_timer = QPushButton("Set")
            self.btn_set_timer.setObjectName("secondary")
            self.btn_set_timer.setFixedHeight(34)
            self.btn_set_timer.clicked.connect(self._apply_timer_from_input)
            self.btn_set_timer.setStyleSheet("margin-top:6px; padding:6px 14px;")

        # fila centrada para el input + set justo debajo de los botones (como pediste)
        timer_config_row = QHBoxLayout()
        timer_config_row.addStretch(1)
        timer_config_row.addWidget(self.input_minutes, alignment=Qt.AlignmentFlag.AlignCenter)
        timer_config_row.addWidget(self.btn_set_timer, alignment=Qt.AlignmentFlag.AlignCenter)
        timer_config_row.addStretch(1)
        timer_layout.addLayout(timer_config_row)

        # Pequeño bloque compacto de sonido dentro del timer_card (opcional)
        small_lbl = QLabel("Sonidos")
        small_lbl.setObjectName("muted")
        timer_layout.addWidget(small_lbl)
        # aseguramos que category_selector y track_selector existan (se llenan más abajo)
        if not hasattr(self, "category_selector"):
            self.category_selector = QComboBox()
        if not hasattr(self, "track_selector"):
            self.track_selector = QComboBox()
        timer_layout.addWidget(self.category_selector)
        timer_layout.addWidget(self.track_selector)

        # BARRA DE VOLUMEN
        volume_layout = QHBoxLayout()
        volume_label = QLabel("Volumen:")
        volume_label.setObjectName("muted")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)  # Volumen por defecto al 50%
        self.volume_slider.valueChanged.connect(self.on_volume_change)
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)
        timer_layout.addLayout(volume_layout)

        # Center container para centrar verticalmente el timer_card
        center_container = QWidget()
        center_layout = QVBoxLayout(center_container)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        center_container.setLayout(center_layout)
        center_layout.addWidget(timer_card, alignment=Qt.AlignmentFlag.AlignCenter)

        # guardar referencia y añadir al dash_layout solo si no está añadido aún
        self.center_container = center_container
        # Antes de añadir, comprobamos si dash_layout ya contiene algo con center_container (evita duplicados)
        already_added = False
        for i in range(self.dash_layout.count()):
            item = self.dash_layout.itemAt(i)
            w = item.widget()
            if w is center_container:
                already_added = True
                break
        if not already_added:
            # añadimos el centro al dash_layout en la posición que quieras (aquí 0 = antes del right)
            self.dash_layout.addWidget(center_container, 2)


        # ----------------- RIGHT COLUMN: monitor + score -----------------
        right_col = QVBoxLayout()
        right_col.addWidget(QLabel("Monitor de Apps (en vivo)"))
        self.list_apps = QListWidget()
        right_col.addWidget(self.list_apps)

        # CircleScore
        self.circle_score = CircleScore(size=110)
        self.circle_score.setValue(100)
        right_col.addWidget(self.circle_score, alignment=Qt.AlignmentFlag.AlignCenter)

        right_col.addWidget(QLabel("Score de sesión"), alignment=Qt.AlignmentFlag.AlignCenter)
        self.label_score = QLabel("Score: 100")
        self.label_score.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_col.addWidget(self.label_score)

        right_widget = QWidget()
        right_widget.setLayout(right_col)
        right_widget.setObjectName("card")
        shadow2 = QGraphicsDropShadowEffect()
        shadow2.setBlurRadius(12)
        shadow2.setOffset(0, 4)
        shadow2.setColor(QColor(0, 0, 0, 120))
        right_widget.setGraphicsEffect(shadow2)

        # --- Añadir columnas al layout del dashboard (LEFT area removed) ---
        # ahora el layout tiene: left_panel (sidebar) | center_container (timer) | right_widget (monitor)
        dash_layout.addWidget(center_container, 2)
        dash_layout.addWidget(right_widget, 1)

        # --- Añadir página al stack ---
        self.stack.addWidget(self.page_dashboard)

        # === Poblar categorías y pistas al iniciar (robusto, con fallback) ===
        # Limpia primero
        try:
            self.category_selector.clear()
            self.track_selector.clear()
        except Exception:
            # si aún no existen en este punto, crea placeholders rápidos
            if not hasattr(self, "category_selector"):
                self.category_selector = QComboBox()
            if not hasattr(self, "track_selector"):
                self.track_selector = QComboBox()

        # Obtener categorías desde AudioManager si implementa get_categories(),
        # sino intentar deducirlas desde self.audio.presets o desde folders en assets/sounds
        cats = []
        try:
            if hasattr(self.audio, "get_categories"):
                cats = list(self.audio.get_categories())
            elif hasattr(self.audio, "presets"):
                # si presets es mapping nombre->file(s)
                cats = list(self.audio.presets.keys())
            else:
                # intentar leer carpetas en assets/sounds
                assets_sounds = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "sounds")
                if os.path.isdir(assets_sounds):
                    cats = [d for d in os.listdir(assets_sounds) if os.path.isdir(os.path.join(assets_sounds, d))]
        except Exception:
            cats = []

        if not cats:
            cats = ["Rain", "Deep Focus", "Dreamscapes"]

        self.category_selector.clear()
        self.category_selector.addItems(cats)

        # Helper local para rellenar pistas — usa audio.get_tracks() si existe,
        # si no intenta deducir pista(s) desde presets o carpeta categoría.
        def _fill_tracks_for_category(cat):
            self.track_selector.clear()
            tracks = []
            try:
                # SOLO intentar usar audio si ya está inicializado
                if hasattr(self, 'audio') and hasattr(self.audio, "get_tracks"):
                    tracks = list(self.audio.get_tracks(cat))
                else:
                    # Fallback: leer del filesystem directamente
                    folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "sounds", cat))
                    if os.path.isdir(folder):
                        for f in sorted(os.listdir(folder)):
                            if f.lower().endswith((".wav", ".mp3", ".ogg")):
                                tracks.append(f)
            except Exception as e:
                print("[DEBUG] Error llenando tracks:", e)
                tracks = []

            # poner items legibles en el combobox y guardar filename en data
            for t in tracks:
                # etiqueta limpia (sin extension)
                label = os.path.splitext(t)[0].replace("_", " ").title()
                self.track_selector.addItem(label, t)

            # si hay pistas, seleccionar la primera y (opcional) no reproducir automáticamente
            if self.track_selector.count() > 0:
                self.track_selector.setCurrentIndex(0)

        # Conectar cambio de categoría -> rellena pistas
        self.category_selector.currentIndexChanged.connect(lambda i: _fill_tracks_for_category(self.category_selector.currentText()))

        # Inicializar con la categoría actual visible
        if self.category_selector.count() > 0:
            _fill_tracks_for_category(self.category_selector.currentText())

        # Conectar cambio de pista -> reproducir (usa play_track si existe, sino play_preset o play_preset fallback)
        def _on_track_selected(index):
            if index < 0:
                return
            filename = self.track_selector.itemData(index)
            cat = self.category_selector.currentText() if hasattr(self, "category_selector") else None
            try:
                if filename:
                    # si AudioManager expone play_track(category, filename)
                    if hasattr(self.audio, "play_track"):
                        self.audio.play_track(cat, filename)
                    else:
                        # si play_preset espera nombre de preset (categoria) y presets mappea a archivo-list
                        if hasattr(self.audio, "play_preset"):
                            # intentar reproducir preset si coincide
                            try:
                                self.audio.play_preset(cat)
                            except Exception:
                                # como fallback carga el archivo directamente si existe play method simple
                                if hasattr(self.audio, "play"):
                                    self.audio.play(os.path.join(cat, filename) if cat else filename)
                        elif hasattr(self.audio, "play"):
                            # método genérico "play" (cargar path)
                            # construye ruta si existe carpeta
                            p = filename
                            # si filename no es absoluto, busca en assets/sounds/<cat> o assets/sounds
                            if not os.path.isabs(p):
                                cand = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "sounds", cat or "", filename))
                                if os.path.exists(cand):
                                    p = cand
                                else:
                                    cand2 = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "sounds", filename))
                                    if os.path.exists(cand2):
                                        p = cand2
                            try:
                                self.audio.play(p)
                            except Exception as e:
                                print("[Audio] play fallback error:", e)
            except Exception as e:
                print("[Audio] on_track_selected error:", e)

        self.track_selector.currentIndexChanged.connect(_on_track_selected)
        
        # Crear las páginas reales
        self.sessions_page = SessionsPage()      # Índice 1
        self.stats_page = StatsPage(self.theme_manager)   # Pasar el theme_manager
        self.presets_page = QWidget()            # Índice 3 - Presets
        self.config_page = QWidget()             # Índice 4 - Configuración

        # Añadir páginas al stack
        self.stack.addWidget(self.page_dashboard)    # Índice 0 - Dashboard
        self.stack.addWidget(self.sessions_page)     # Índice 1 - Sesiones  
        self.stack.addWidget(self.stats_page)        # Índice 2 - Estadísticas
        self.stack.addWidget(self.presets_page)      # Índice 3 - Presets
        self.stack.addWidget(self.config_page)       # Índice 4 - Configuración

        # Setup de las páginas
        self._setup_presets_page()
        self._setup_config_page()

    # ========== SETUP FUNCTIONS FOR PAGES ==========

    def _setup_presets_page(self):
        """Página de Presets - Placeholder"""
        layout = QVBoxLayout()
        self.presets_page.setLayout(layout)
        
        # Widget contenedor con estilo
        container = QWidget()
        container.setObjectName("soon_container")
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)
        
        # Cargar imagen "pronto.png" desde assets
        soon_label = QLabel()
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "pronto.png"))
        if os.path.exists(icon_path):
            soon_pixmap = QPixmap(icon_path).scaled(600, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            soon_label.setPixmap(soon_pixmap)
        else:
            soon_label.setText("Pronto")
            soon_label.setStyleSheet("font-size: 48px; color: rgba(124,58,237,0.7); font-weight: bold;")
        
        soon_label.setAlignment(Qt.AlignCenter)
        soon_label.setObjectName("soon_label")
        
        container_layout.addWidget(soon_label)
        layout.addWidget(container)

    def _setup_config_page(self):
        """Página de Configuración - Placeholder"""
        layout = QVBoxLayout()
        self.config_page.setLayout(layout)
        
        # Widget contenedor con estilo
        container = QWidget()
        container.setObjectName("soon_container")
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)
        
        # Cargar imagen "pronto.png" desde assets
        soon_label = QLabel()
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "pronto.png"))
        if os.path.exists(icon_path):
            soon_pixmap = QPixmap(icon_path).scaled(600, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            soon_label.setPixmap(soon_pixmap)
        else:
            soon_label.setText("Pronto")
            soon_label.setStyleSheet("font-size: 48px; color: rgba(124,58,237,0.7); font-weight: bold;")
        
        soon_label.setAlignment(Qt.AlignCenter)
        soon_label.setObjectName("soon_label")
        
        container_layout.addWidget(soon_label)
        layout.addWidget(container)

    # ---------- Slots / callbacks ----------

    @Slot()
    def on_start(self):
        # Aplicar configuración actual antes de arrancar
        try:
            # Si hay una pista seleccionada, usarla
            if hasattr(self, "track_selector") and self.track_selector.count() > 0:
                idx = self.track_selector.currentIndex()
                filename = self.track_selector.itemData(idx)
                cat = self.category_selector.currentText() if hasattr(self, "category_selector") else None
                if filename and cat:
                    if self.audio.is_paused():
                        self.audio.resume_all()
                    else:
                        # VERIFICAR que el método existe antes de llamarlo
                        if hasattr(self.audio, "play_track"):
                            self.audio.play_track(cat, filename)
                        else:
                            print("[WARN] audio.play_track no disponible")
        except Exception as e:
            print("[WARN] audio start/resume error:", e)

        # Resto del código igual...
        self.pomodoro.start()

        #GUARDAR TIEMPO DE INICIO
        self.session_start_time = datetime.datetime.now()
        print(f"⏰ [SESSION] Inicio guardado: {self.session_start_time}")
        
        if not self._tracker_running:
            self.tracker.start()
            self._tracker_running = True
            self._last_active_ts = time.time()


    @Slot()
    def on_pause(self):
        self.pomodoro.pause()
        try:
            # pausar audio (no stop)
            self.audio.pause_all()
            self._audio_paused = True
        except Exception as e:
            print("[WARN] audio pause error:", e)
        # detener tracker y salvar último intervalo
        self._stop_tracker_and_flush()


    @Slot()
    def on_reset(self):
        self.pomodoro.reset()
        self.label_timer.setText(self.pomodoro.format_time())
        try:
            self.audio.stop_all()
            self._audio_paused = False
        except Exception as e:
            print("[WARN] audio stop error:", e)
        
        # RESETEAR TIEMPO DE INICIO
        self.session_start_time = None
        
        # GUARDAR SESIÓN TAMBIÉN EN RESET SI HAY TIEMPO
        if hasattr(self.pomodoro, 'elapsed_seconds') and self.pomodoro.elapsed_seconds > 30:
            print("[DEBUG] Reset con tiempo acumulado - Guardando sesión...")
            self._save_session()
        
        # Resetear notificaciones de score
        self.scorer.last_notified_score = 100
        
        # Limpiar historial de apps
        self.list_apps.clear()
        self.last_app_key = None
        self.app_history.clear()
        
        # detener tracker y flush
        self._stop_tracker_and_flush()


    @Slot(int)
    def on_volume_change(self, val):
        # Convertir de 0-100 a 0.0-1.0 para pygame
        volume = val / 100.0
        try:
            self.audio.set_master_volume(volume)
        except Exception as e:
            print("[WARN] Error cambiando volumen:", e)

    @Slot(int, int)
    def on_tick(self, minutes, seconds):
        """Actualiza el timer visual desde la señal del pomodoro y refresca el score."""
        # actualiza el timer grande
        try:
            self.label_timer.setText(f"{minutes:02d}:{seconds:02d}")
        except Exception:
            pass

        # actualizar progress si existe
        try:
            total = getattr(self.pomodoro, "total_seconds", None)
            remaining = getattr(self.pomodoro, "remaining", None)
            if total and remaining is not None and hasattr(self, "session_progress"):
                done = total - remaining
                percent = int((done / total) * 100) if total > 0 else 0
                self.session_progress.setValue(percent)
        except Exception:
            pass

        # ---- actualizar score usando el nuevo método progresivo ----
        try:
            score = self.get_progressive_score()   #
            # actualizar label y círculo (si existen)
            if hasattr(self, "label_score"):
                self.label_score.setText(f"Score: {score}")
            if hasattr(self, "circle_score"):
                self.circle_score.setValue(score)

            self.scorer._check_score_notification(score)
        except Exception as e:
            # no queremos romper el tick por un fallo en scorer
            print("[WARN] on_tick -> error actualizando score:", e)



    @Slot()
    def on_pomodoro_finished(self):
        print("🎯 [DEBUG] on_pomodoro_finished SE EJECUTÓ")
        print(f"🎯 [DEBUG] Tiempo transcurrido ANTES de notificar: {getattr(self.pomodoro, 'elapsed_seconds', 'NO EXISTE')}")
        
        self.notifier.notify("Pomodoro terminado", kind="info")
        self.audio.stop_all()
        
        # ⭐⭐ GUARDAR SESIÓN AL TERMINAR ⭐⭐
        self._save_session()
        
        # flush final intervalo
        self._stop_tracker_and_flush()

    @Slot(str, str)
    def on_active_changed(self, process, title):
        """
        Este slot es llamado por AppTracker cuando cambia la ventana activa.
        """
        now = time.time()
        
        # Si hay un último proceso conocido, calcular delta y enviar al scorer
        if self._last_active_proc is not None and self._last_active_ts is not None:
            delta = int(now - self._last_active_ts)
            if delta > 1:  # Solo si el delta es significativo (más de 1 segundo)
                self.scorer.push_active(self._last_active_proc, self._last_active_title, delta)
        
        # Actualizar el último proceso
        self._last_active_proc = process or ""
        self._last_active_title = title or ""
        self._last_active_ts = now
        
        # Actualizar lista visual COMPACTADA
        self._update_compact_app_list(process, title)

    def _update_compact_app_list(self, process, title):
        """Actualiza la lista de apps de forma compacta mostrando tiempo acumulado"""
        try:
            current_key = (process or "unknown", title or "")
            
            if current_key not in self.app_history:
                self.app_history[current_key] = 0
            self.app_history[current_key] += 2  # Sumar 2 segundos (intervalo del tracker)
            
            print(f"[DEBUG] App history: {len(self.app_history)} apps, {self.app_history.get(current_key, 0)}s en {current_key}")

            # Si es la misma app que la última, actualizar tiempo
            if current_key == self.last_app_key and self.list_apps.count() > 0:
                # Actualizar el último item
                last_item = self.list_apps.item(0)
                if last_item:
                    current_text = last_item.text()
                    # Extraer el tiempo actual y sumar 2 segundos (intervalo del tracker)
                    if "| T:" in current_text:
                        parts = current_text.split("| T:")
                        if len(parts) == 2:
                            base_text = parts[0].strip()
                            # Buscar el tiempo en el texto
                            time_match = re.search(r'(\d+)s', parts[1])
                            if time_match:
                                current_seconds = int(time_match.group(1)) + 2
                                new_text = f"{base_text} | T: {current_seconds}s"
                                last_item.setText(new_text)
                    return
            
            # Si es una app nueva, resetear last_app_key y agregar nueva línea
            self.last_app_key = current_key
            
            # Formatear el texto de la app
            proc_display = process or "unknown"
            title_display = title or ""
            
            # Limitar longitud del título si es muy largo
            if len(title_display) > 40:
                title_display = title_display[:37] + "..."
            
            item_text = f"{proc_display} | {title_display} | T: 2s"
            
            # Insertar al inicio
            self.list_apps.insertItem(0, item_text)
            
            # Limitar a 20 items máximo
            if self.list_apps.count() > 20:
                self.list_apps.takeItem(20)
                
        except Exception as e:
            print(f"[AppList] Error actualizando lista: {e}")

    def _stop_tracker_and_flush(self):
        """
        Detener el tracker (si está corriendo) y enviar el último intervalo
        que quedó abierto hasta el momento de detenerlo.
        """
        if self._tracker_running:
            # calcular delta final
            now = time.time()
            if self._last_active_proc is not None and self._last_active_ts is not None:
                delta = int(now - self._last_active_ts)
                if delta > 0:
                    self.scorer.push_active(self._last_active_proc, self._last_active_title, seconds=delta)

            try:
                self.tracker.stop()
            except Exception:
                pass
            self._tracker_running = False
            self._last_active_proc = None
            self._last_active_title = None
            self._last_active_ts = None

    def _save_session(self):
        """Guardar datos de la sesión completada"""
        try:
            print("[DEBUG] Ejecutando _save_session...")
            
            # CALCULAR DURACIÓN MANUALMENTE
            if self.session_start_time:
                end_time = datetime.datetime.now()
                duration = int((end_time - self.session_start_time).total_seconds())
                start_time = self.session_start_time
                print(f"⏰ [SESSION] Duración manual: {duration}s (desde {start_time})")
            else:
                # Fallback al método del pomodoro
                duration = getattr(self.pomodoro, 'elapsed_seconds', 0)
                start_time = datetime.datetime.now() - datetime.timedelta(seconds=duration)
                end_time = datetime.datetime.now()
                print(f"⏰ [SESSION] Duración fallback: {duration}s")
            
            if duration < 10:  # Menos de 10 segundos no guardar
                print(f"❌ [SESSION] Duración muy corta ({duration}s), no se guarda sesión")
                return
                
            final_score = self.get_progressive_score()
            
            print(f"✅ [SESSION] Guardando sesión - Duración: {duration}s, Score: {final_score}%")
            
            # Preparar datos de apps
            app_data = []
            if hasattr(self, 'app_history'):
                for (proc, title), seconds in self.app_history.items():
                    if seconds > 5:  # Solo apps con más de 5 segundos
                        app_data.append((proc, title, seconds))
            
            print(f"📱 [SESSION] Apps registradas: {len(app_data)}")
            
            # Guardar en base de datos
            apps_used_str = ", ".join([f"{proc}({secs}s)" for proc, title, secs in app_data[:5]])
            session_id = database.save_session(
                start_time.isoformat(),
                end_time.isoformat(),
                duration,
                final_score,
                apps_used_str
            )
            
            # Guardar apps individuales
            database.save_session_apps(session_id, app_data)
            
            print(f"🎉 [SESSION] Sesión guardada - ID: {session_id}, Duración: {duration}s, Score: {final_score}%")
            
            # ⭐⭐ RESETEAR TIEMPO DE INICIO ⭐⭐
            self.session_start_time = None
            
        except Exception as e:
            print(f"❌ [SESSION] Error guardando sesión: {e}")
            import traceback
            traceback.print_exc()


    def _apply_timer_from_input(self):
        """Aplica la duración ingresada en input_minutes al pomodoro."""
        minutes = int(self.input_minutes.value())
        seconds = minutes * 60
        # intentamos llamar a una API del Pomodoro si existe
        try:
            if hasattr(self.pomodoro, "set_duration"):
                # método explícito preferido en tu clase Pomodoro
                self.pomodoro.set_duration(seconds)
            else:
                # fallback: setear atributos si tu Pomodoro usa estos nombres
                if hasattr(self.pomodoro, "default_minutes"):
                    self.pomodoro.default_minutes = minutes
                if hasattr(self.pomodoro, "remaining"):
                    self.pomodoro.remaining = seconds
                if hasattr(self.pomodoro, "total_seconds"):
                    self.pomodoro.total_seconds = seconds
        except Exception as e:
            print("[WARN] no se pudo setear la duración en Pomodoro:", e)

        # actualizar display grande
        mm = minutes
        self.label_timer.setText(f"{mm:02d}:00")
        # si tienes progress bar, resetearla aquí (si aplica):
        try:
            if hasattr(self, "session_progress"):
                self.session_progress.setValue(0)
        except Exception:
            pass


    @Slot(str, str)
    def on_notify(self, kind, message):
        # placeholder: mostrar en console por ahora
        print(f"[NOTIFY] {kind}: {message}")


    @Slot(int)
    def on_nav_changed(self, index):
        self.stack.setCurrentIndex(index)
        # si estamos en Dashboard (index == 0) dejar el timer centrado
        if hasattr(self, "dash_layout") and hasattr(self, "timer_card"):
            if index == 0:
                # centro: timer compacto
                self.timer_card.setMaximumWidth(380)
                # hacer que el centro ocupe menos (1) y right 1
                self.dash_layout.setStretch(0, 1)  # centro column
                self.dash_layout.setStretch(1, 1)  # right column
            else:
                # al moverse a otra página, expandir timer_card hacia la derecha (más espacio)
                self.timer_card.setMaximumWidth(520)
                # hacemos que el centro ocupe más espacio
                self.dash_layout.setStretch(0, 2)
                self.dash_layout.setStretch(1, 1)


    # Theme toggle slot
    def on_toggle_theme(self):
        # alterna tema y cambia el icono/texto del botón
        self.theme_manager.toggle()
        if self.theme_manager.dark:
            self.theme_toggle.setText("🌙")
        else:
            self.theme_toggle.setText("☀️")


if __name__ == "__main__":
    print(">>> main_window.py arrancó")
    app = QApplication(sys.argv)
    window = FocuslyMain()
    window.show()
    sys.exit(app.exec())


