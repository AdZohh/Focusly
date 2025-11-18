# src/ui/stats_page.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from PySide6.QtCharts import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from data import database
import datetime

class StatsPage(QWidget):
    def __init__(self, theme_manager=None):
        super().__init__()
        self.theme_manager = theme_manager  # Guardar referencia
        self.stats_data = None
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.metrics_grid = QGridLayout()

        self._setup_ui()
        self.load_stats()
        
    def _setup_ui(self):
        # Header con título y botón
        header_layout = QHBoxLayout()
        
        title = QLabel("Estadísticas de Productividad")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Botón Actualizar
        refresh_btn = QPushButton("🔄 Actualizar")
        refresh_btn.clicked.connect(self.load_stats)
        refresh_btn.setStyleSheet('''
            QPushButton {
                background: rgba(124,58,237,0.2);
                color: white;
                border: 1px solid rgba(124,58,237,0.4);
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(124,58,237,0.3);
            }
        ''')
        
        header_layout.addWidget(refresh_btn)
        self.layout.addLayout(header_layout)
        
        #AGREGAR metrics_grid AL LAYOUT PRINCIPAL
        self.layout.addLayout(self.metrics_grid)
        
        # Gráficos
        self.charts_layout = QHBoxLayout()
        self.layout.addLayout(self.charts_layout)
        
    def load_stats(self):
        """Cargar y mostrar estadísticas"""
        print("📊 [STATS] Cargando estadísticas...")
        
        # ⭐⭐ LIMPIAR LAYOUTS EXISTENTES ⭐⭐
        self._clear_layout(self.metrics_grid)
        self._clear_layout(self.charts_layout)
        
        sessions = database.get_all_sessions()
        
        if not sessions:
            no_data_label = QLabel("No hay datos de sesiones todavía. ¡Completa algunas sesiones!")
            no_data_label.setAlignment(Qt.AlignCenter)
            no_data_label.setStyleSheet("font-size: 16px; color: #9aa0c7; padding: 40px;")
            self.layout.addWidget(no_data_label)
            return
        
        # Calcular métricas
        total_sessions = len(sessions)
        total_time = sum(session[3] for session in sessions)  # duration_seconds
        avg_score = sum(session[4] for session in sessions) / total_sessions  # final_score
        best_score = max(session[4] for session in sessions)
        
        # Mostrar métricas
        metrics = [
            ("Sesiones Totales", f"{total_sessions}"),
            ("Tiempo Total", f"{total_time//3600}h {(total_time%3600)//60}m"),
            ("Score Promedio", f"{avg_score:.1f}%"),
            ("Mejor Score", f"{best_score}%")
        ]
        
        for i, (label, value) in enumerate(metrics):
            metric_widget = self._create_metric_widget(label, value)
            self.metrics_grid.addWidget(metric_widget, i//2, i%2)
        
        # Crear gráficos
        self._create_score_chart(sessions)
        self._create_time_chart(sessions)

    # AGREGAR MÉTODO PARA LIMPIAR LAYOUTS
    def _clear_layout(self, layout):
        """Limpiar todos los widgets de un layout"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
    def _create_metric_widget(self, label, value):
        """Crear widget de métrica individual - SIN ESTILOS INLINE"""
        widget = QWidget()
        widget.setObjectName("metric_card")  # 
        
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        value_label = QLabel(value)
        value_label.setObjectName("metric_value")  # 
        value_label.setAlignment(Qt.AlignCenter)
        
        label_label = QLabel(label)
        label_label.setObjectName("metric_label")  # 
        label_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(value_label)
        layout.addWidget(label_label)
        
        return widget
        
    def _create_score_chart(self, sessions):
        """Crear gráfico de scores por sesión"""
        series = QBarSeries()
        
        bar_set = QBarSet("Score")
        dates = []
        
        # Últimas 10 sesiones
        recent_sessions = sessions[:10]
        
        for session in reversed(recent_sessions):  # Más antiguo a más reciente
            session_id, start_time, end_time, duration, score, apps_used = session
            start_dt = datetime.datetime.fromisoformat(start_time)
            dates.append(start_dt.strftime("%d/%m"))
            bar_set.append(score)
        
        bar_set.setColor("#7c3aed")
        series.append(bar_set)
        
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Scores por Sesión (Últimas 10)")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        axis_x = QBarCategoryAxis()
        axis_x.append(dates)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setRange(0, 100)
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumSize(400, 300)
        
        self.charts_layout.addWidget(chart_view)
        
    def _create_time_chart(self, sessions):
        """Crear gráfico de tiempo por aplicación"""
        # Agrupar tiempo por aplicación
        app_time = {}
        for session in sessions:
            session_id = session[0]
            session_apps = database.get_session_apps(session_id)
            
            for app_name, app_title, app_seconds in session_apps:
                if app_name not in app_time:
                    app_time[app_name] = 0
                app_time[app_name] += app_seconds
        
        # Tomar top 5 apps
        top_apps = sorted(app_time.items(), key=lambda x: x[1], reverse=True)[:5]
        
        if not top_apps:
            return
            
        series = QPieSeries()
        
        for app_name, total_seconds in top_apps:
            minutes = total_seconds // 60
            slice = series.append(f"{app_name} ({minutes}m)", total_seconds)
            slice.setColor(self._get_color_for_app(app_name))
        
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Tiempo por Aplicación (Top 5)")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumSize(400, 300)
        
        self.charts_layout.addWidget(chart_view)
        
    def _get_color_for_app(self, app_name):
        """Color consistente para cada aplicación"""
        colors = ["#7c3aed", "#ec4899", "#8b5cf6", "#06b6d4", "#10b981"]
        app_hash = hash(app_name) % len(colors)
        return colors[app_hash]