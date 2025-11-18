# src/ui/sessions_page.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QListWidget, QPushButton, QTextEdit, QSplitter,
                              QMessageBox, QScrollArea)
from PySide6.QtCore import Qt
from data import database
import datetime
import sqlite3
import os

class SessionsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self._setup_ui()
        self.load_sessions()
        
    def _setup_ui(self):
        # Header con título y botones
        header_layout = QHBoxLayout()
        
        title = QLabel("Historial de Sesiones")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Botón Actualizar
        refresh_btn = QPushButton("🔄 Actualizar")
        refresh_btn.clicked.connect(self.load_sessions)
        refresh_btn.setStyleSheet("""
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
        """)
        
        # Botón Limpiar Historial
        clear_btn = QPushButton("🗑️ Limpiar")
        clear_btn.clicked.connect(self.clear_history)
        clear_btn.setStyleSheet("""
            QPushButton {
                background: rgba(239,68,68,0.2);
                color: white;
                border: 1px solid rgba(239,68,68,0.4);
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(239,68,68,0.3);
            }
        """)
        
        header_layout.addWidget(refresh_btn)
        header_layout.addWidget(clear_btn)
        
        self.layout.addLayout(header_layout)
        
        # Splitter para lista y detalles
        splitter = QSplitter(Qt.Horizontal)
        
        # PRIMERO CREAR AMBOS WIDGETS ANTES DE AGREGARLOS AL SPLITTER
        
        # Lista de sesiones
        sessions_container = QWidget()
        sessions_layout = QVBoxLayout()
        sessions_container.setLayout(sessions_layout)
        
        sessions_layout.addWidget(QLabel("Sesiones Guardadas:"))
        self.sessions_list = QListWidget()
        self.sessions_list.itemClicked.connect(self.on_session_selected)
        sessions_layout.addWidget(self.sessions_list)
        
        # Detalles de sesión
        self.details_widget = QWidget() 
        details_layout = QVBoxLayout()
        self.details_widget.setLayout(details_layout)

        details_layout.addWidget(QLabel("Detalles de Sesión:"))

        self.session_details = QTextEdit()
        self.session_details.setReadOnly(True)
        self.session_details.setObjectName("session_details_card")  # 

        details_layout.addWidget(self.session_details)

        splitter.addWidget(sessions_container)
        splitter.addWidget(self.details_widget)

        splitter.setSizes([400, 600])

        self.layout.addWidget(splitter)
        
    def load_sessions(self):
        """Cargar todas las sesiones desde la base de datos"""
        self.sessions_list.clear()
        sessions = database.get_all_sessions()
        
        if not sessions:
            self.sessions_list.addItem("No hay sesiones guardadas todavía")
            self.session_details.clear()
            return
        
        for session in sessions:
            session_id, start_time, end_time, duration, score, apps_used = session
            
            # FILTRAR SESIONES CON DURACIÓN VÁLIDA
            if duration < 10:  # Menos de 10 segundos no mostrar
                continue
                
            # Formatear fecha
            start_dt = datetime.datetime.fromisoformat(start_time)
            date_str = start_dt.strftime("%d/%m/%Y %H:%M")
            
            # Duración en minutos
            minutes = duration // 60
            seconds = duration % 60
            
            item_text = f"{date_str} - {minutes}min {seconds}s - Score: {score}%"
            self.sessions_list.addItem(item_text)
            self.sessions_list.item(self.sessions_list.count()-1).setData(Qt.UserRole, session_id)
            
    def on_session_selected(self, item):
        """Mostrar detalles de la sesión seleccionada"""
        session_id = item.data(Qt.UserRole)
        sessions = database.get_all_sessions()
        
        # Encontrar la sesión seleccionada
        selected_session = None
        for session in sessions:
            if session[0] == session_id:
                selected_session = session
                break
        
        if selected_session:
            session_id, start_time, end_time, duration, score, apps_used = selected_session
            
            # Formatear detalles con MEJOR FORMATO
            start_dt = datetime.datetime.fromisoformat(start_time)
            end_dt = datetime.datetime.fromisoformat(end_time)
            
            # Calcular duración formateada
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            seconds = duration % 60
            
            duration_str = f"{minutes}min {seconds}s"
            if hours > 0:
                duration_str = f"{hours}h {minutes}min"
            
            details = f"""
<div style="font-family: 'Segoe UI', Arial; line-height: 1.6;">
    
    <div style="background: rgba(124,58,237,0.1); padding: 15px; border-radius: 10px; margin-bottom: 15px;">
        <h2 style="margin: 0; color: #8b5cf6;">🏁 SESIÓN COMPLETADA</h2>
    </div>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
        <div style="background: rgba(255,255,255,0.05); padding: 12px; border-radius: 8px;">
            <strong>📅 Fecha:</strong><br>{start_dt.strftime("%d/%m/%Y")}
        </div>
        <div style="background: rgba(255,255,255,0.05); padding: 12px; border-radius: 8px;">
            <strong>⏰ Horario:</strong><br>{start_dt.strftime("%H:%M")} - {end_dt.strftime("%H:%M")}
        </div>
        <div style="background: rgba(255,255,255,0.05); padding: 12px; border-radius: 8px;">
            <strong>⏱️ Duración:</strong><br>{duration_str}
        </div>
        <div style="background: rgba(255,255,255,0.05); padding: 12px; border-radius: 8px;">
            <strong>🎯 Score Final:</strong><br>{score}%
        </div>
    </div>
    
    <div style="background: rgba(139,92,246,0.1); padding: 15px; border-radius: 10px;">
        <h3 style="margin: 0 0 10px 0; color: #a78bfa;">📊 APLICACIONES UTILIZADAS</h3>
"""
            # Obtener apps de esta sesión
            session_apps = database.get_session_apps(session_id)
            
            if session_apps:
                # Ordenar por tiempo (mayor a menor)
                session_apps.sort(key=lambda x: x[2], reverse=True)
                
                for app_name, app_title, app_seconds in session_apps:
                    app_minutes = app_seconds // 60
                    app_secs = app_seconds % 60
                    
                    time_str = f"{app_minutes}m {app_secs}s"
                    if app_minutes == 0:
                        time_str = f"{app_secs}s"
                    elif app_minutes > 60:
                        hours = app_minutes // 60
                        mins = app_minutes % 60
                        time_str = f"{hours}h {mins}m"
                    
                    # Limitar título largo
                    display_title = app_title
                    if len(display_title) > 60:
                        display_title = display_title[:57] + "..."
                    
                    details += f"""
        <div style="background: rgba(255,255,255,0.03); padding: 10px; margin: 5px 0; border-radius: 6px; border-left: 3px solid #7c3aed;">
            <strong>{app_name}</strong><br>
            <span style="color: #9aa0c7; font-size: 12px;">{display_title}</span><br>
            <span style="color: #8b5cf6; font-weight: bold;">⏱️ {time_str}</span>
        </div>"""
            else:
                details += """
        <div style="text-align: center; color: #9aa0c7; padding: 20px;">
            No hay datos de aplicaciones para esta sesión
        </div>"""
            
            details += """
    </div>
    
</div>
"""
            self.session_details.setHtml(details)
            
    def clear_history(self):
        """Limpiar todo el historial de sesiones"""
        reply = QMessageBox.question(self, "Limpiar Historial", 
                                   "¿Estás seguro de que quieres eliminar TODAS las sesiones?\nEsta acción no se puede deshacer.",
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                # Eliminar archivo de base de datos
                db_path = os.path.join(os.path.dirname(__file__), "..", "..", "focusly.db")
                if os.path.exists(db_path):
                    os.remove(db_path)
                    print("✅ Historial de sesiones eliminado")
                    
                    # Recargar la base de datos vacía
                    import data.database
                    data.database.init_db()
                    
                    # Recargar la lista
                    self.load_sessions()
                    self.session_details.clear()
                    
                    QMessageBox.information(self, "Listo", "Historial eliminado correctamente")
                else:
                    QMessageBox.warning(self, "Error", "No se encontró la base de datos")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar el historial: {str(e)}")