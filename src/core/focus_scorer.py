# src/core/focus_scorer.py
import time
import re
import csv
from collections import deque
from typing import List, Optional, Tuple
from PySide6.QtCore import QObject, Signal

class FocusScorer(QObject):
    """
    Scorer basado en ventana temporal (sliding window).
    - push_active(proc, title, seconds): registra un intervalo de actividad
    - get_current_score(window_seconds=1800): calcula el score en la ventana
    - configurable: productive list, distractors list, umbral de distracción por chunk
    - util: exportar historial, resetear, añadir/quitar palabras
    """
    distraction_detected = Signal(str, str, int)

    def __init__(
        self,
        productive_list: Optional[List[str]] = None,
        distracting_list: Optional[List[str]] = None,
        window_seconds: int = 1800,
        distractor_threshold_seconds: int = 60,
    ):
        super().__init__()  
        
        # default heuristics (puedes ampliar)
        self.productive = [p.lower() for p in (productive_list or [
            "code", "visual studio", "pycharm", "sublime", "vscode", "word", "google docs", "excel", "matlab",
            "jupyter", "notepad", "terminal", "powershell", "spyder"
        ])]
        self.distractors = [d.lower() for d in (distracting_list or [
            "youtube", "facebook", "instagram", "netflix", "tiktok", "discord", "reddit", "twitter", "steam"
        ])]

        # historial como deque de items (start_ts, end_ts, proc, title, seconds)
        self.history = deque()
        self.window_seconds = window_seconds
        self.distractor_threshold_seconds = distractor_threshold_seconds
        
        # AGREGAR: Variables para notificaciones
        self.last_notification_time = 0
        self.notification_cooldown = 30

        # NUEVO: Para notificaciones cada 5%
        self.last_notified_score = 100  # Empezamos en 100%
        self.notification_threshold = 5  # Cada 5%

    # En focus_scorer.py - AGREGAR este método:

    def _check_score_notification(self, current_score: int):
        """
        Notifica SOLO cuando el score llega exactamente a umbrales de 5%
        """
        try:
            print(f"[SCORE CHECK] Score: {current_score}% | Último: {self.last_notified_score}%")
            
            # ⭐⭐ CONDICIÓN MÁS SIMPLE: Solo notificar en múltiplos exactos de 5 ⭐⭐
            if current_score % 5 == 0 and current_score < self.last_notified_score:
                print(f"✅ NOTIFICANDO {current_score}%")
                message = self._get_notification_message(current_score)
                self.distraction_detected.emit("score_alert", message, 0)
                self.last_notified_score = current_score
            
            # Resetear cuando el score suba por encima del último notificado
            elif current_score > self.last_notified_score:
                print(f"🔼 Score subió a {current_score}%, reseteando notificaciones")
                self.last_notified_score = current_score
                
        except Exception as e:
            print("[FocusScorer] Error en notificación de score:", e)


    # En _get_notification_message - mensajes más cortos para ventanas:

    def _get_notification_message(self, threshold: int) -> str:
        """Mensajes personalizados para notificaciones visuales"""
        messages = {
            95: "Focus al 95% - ¡Vas bien! Mantén la concentración 💪",
            90: "Focus al 90% - Sigue enfocado en tu tarea 🎯", 
            85: "Focus al 85% - ¡Tú puedes mantener el ritmo! ⚡",
            80: "Focus al 80% - Recuerda tu objetivo principal 🎯",
            75: "Focus al 75% - Las distracciones están ganando ⏰",
            70: "Focus al 70% - ¡Reacciona a tiempo! Vuelve al trabajo 🔄",
            65: "Focus al 65% - Tu productividad está bajando 📉",
            60: "Focus al 60% - Momento de respirar y reenfocarse 🌬️",
            55: "Focus al 55% - ¡No te rindas! Enfócate de nuevo 💥",
            50: "Focus al 50% - Toma el control de tu sesión 🛡️",
            45: "Focus al 45% - La batalla por el focus continúa ⚔️",
            40: "Focus al 40% - Alerta: Sesión en riesgo 🚨",
            35: "Focus al 35% - ¿Necesitas un descanso programado? 🤔",
            30: "Focus al 30% - Nivel bajo - Considera un break ☕",
            25: "Focus al 25% - Focus muy bajo - ¿Reiniciar sesión? 🔄",
            20: "Focus al 20% - ¡Última alerta! Focus crítico 💀",
            15: "Focus al 15% - ¿Estás seguro de querer continuar? ❓",
            10: "Focus al 10% - Nivel mínimo de productividad 📉",
            5: "Focus al 5% - Sesión en estado crítico 🆘"
        }
        return messages.get(threshold, f"Focus: {threshold}%")

    # ------------------ registro ------------------
    def push_active(self, proc: Optional[str], title: Optional[str], seconds: int = 0):
        """
        Registra que la ventana/proceso estuvo activo `seconds` segundos.
        """
        try:
            end_ts = time.time()
            start_ts = end_ts - max(0, int(seconds))
            proc = (proc or "").strip()
            title = (title or "").strip()
            
            # Acumular tiempo para la misma ventana
            if self.history:
                last_start, last_end, last_proc, last_title, last_seconds = self.history[-1]
                if last_proc == proc and last_title == title:
                    # Fusionar con el último evento
                    self.history.pop()
                    start_ts = last_start
                    seconds = int(last_seconds + seconds)
            
            self.history.append((start_ts, end_ts, proc, title, int(seconds)))
            self._prune_old()
            
            # DETECTAR DISTRACCIONES (código existente)
            cls = self._classify_event(start_ts, end_ts, proc, title, int(seconds))
            current_time = time.time()
            
            if (cls == "distractor" and 
                seconds >= 30 and
                (current_time - self.last_notification_time) >= self.notification_cooldown):
                
                self.last_notification_time = current_time
                self.distraction_detected.emit(proc, title, seconds)
                
        except Exception as e:
            print("[FocusScorer] push_active error:", e)

    def _prune_old(self):
        """Eliminar eventos completamente fuera de la ventana actual (usar window_seconds)."""
        cutoff = time.time() - self.window_seconds
        while self.history and self.history[0][1] < cutoff:
            self.history.popleft()

    # ------------------ clasificación ------------------
    def _is_productive(self, proc: str, title: str) -> bool:
        lowp = (proc or "").lower()
        lowt = (title or "").lower()
        return any(k in lowp or k in lowt for k in self.productive)

    def _is_distractor_by_name(self, proc: str, title: str) -> bool:
        lowp = (proc or "").lower()
        lowt = (title or "").strip().lower()
        
        # Detectar por nombre de aplicación
        app_distractors = any(k in lowp or k in lowt for k in self.distractors)
        if app_distractors:
            return True
        
        # MEJORAR detección de navegadores
        browser_keywords = ["chrome", "firefox", "edge", "opera", "safari", "brave", "browser"]
        is_browser = any(k in lowp for k in browser_keywords)
        
        if is_browser:
            # Lista ampliada de sitios web distractores
            website_distractors = [
                "youtube", "youtu.be", "netflix", "twitch", "tiktok", "instagram",
                "facebook", "twitter", "x.com", "reddit", "9gag", "whatsapp",
                "telegram", "discord", "spotify", "pinterest", "tumblr",
                "prime video", "hulu", "disney+", "hbomax", "crunchyroll",
                "facebook.com", "instagram.com", "twitter.com", "x.com"
            ]
            
            # DETECTAR YOUTUBE EN TÍTULOS DE PESTAÑAS
            # Los títulos de YouTube suelen ser: "Nombre del video - YouTube"
            if "youtube" in lowt or " - youtube" in lowt:
                return True
                
            # Detectar otros sitios en el título
            title_has_distractor = any(site in lowt for site in website_distractors)
            if title_has_distractor:
                return True
        
        # DETECTAR VIDEOJUEGOS
        game_processes = [
            "steam", "steamwebhelper", "epicgameslauncher", "minecraft", 
            "roblox", "lol", "league of legends", "valorant", "csgo", 
            "overwatch", "fortnite", "game", "launcher"
        ]
        
        if any(game in lowp for game in game_processes):
            return True
            
        # DETECTAR REPRODUCTORES DE VIDEO/MÚSICA 
        media_players = ["vlc", "spotify", "windowsmediaplayer", "itunes", "quicktime"]
        if any(player in lowp for player in media_players):
            return True
            
        return False

    def _classify_event(self, start_ts: float, end_ts: float, proc: str, title: str, seconds: int) -> str:
        """
        Devuelve: 'productive', 'distractor' o 'neutral'
        """
        classification = "neutral"
        
        if self._is_productive(proc, title):
            classification = "productive"
        elif self._is_distractor_by_name(proc, title):
            classification = "distractor"
        elif seconds >= self.distractor_threshold_seconds:
            classification = "distractor"
        
        return classification

    # ------------------ cálculo del score ------------------
    def get_current_score(self, window_seconds: Optional[int] = None, session_start_time: Optional[float] = None) -> int:
        """
        Calcula el score basado en el tiempo de sesión actual.
        Si se pasa session_start_time, usa esa ventana temporal.
        Si no, usa window_seconds (default 30min).
        """
        # SI TENEMOS TIEMPO DE INICIO DE SESIÓN, USAR ESA VENTANA
        if session_start_time is not None:
            now = time.time()
            session_duration = now - session_start_time
            w = min(session_duration, self.window_seconds)  # No más de la ventana máxima
            cutoff = session_start_time
        else:
            # Ventana fija por defecto
            w = window_seconds or self.window_seconds
            now = time.time()
            cutoff = now - w

        print(f"[SCORE CALC] Ventana: {w}s, Cutoff: {cutoff}")

        # sumar segundos totales y distractores con recuento parcial si el evento cruza frontera
        total = 0.0
        distractor = 0.0

        # recorrer history (ya pruned normalmente pero aquí aseguramos recálculo correcto)
        for start_ts, end_ts, proc, title, seconds in list(self.history):
            # calcular overlap con la ventana [cutoff, now]
            ov_start = max(start_ts, cutoff)
            ov_end = min(end_ts, now)
            if ov_end <= ov_start:
                continue
            ov_seconds = ov_end - ov_start
            total += ov_seconds
            cls = self._classify_event(start_ts, end_ts, proc, title, int(seconds))
            if cls == "distractor":
                distractor += ov_seconds

        # ⭐⭐ PRIMERO CALCULAR RATIO Y SCORE, LUEGO HACER DEBUG ⭐⭐
        if total <= 0:
            return 100
        
        ratio = distractor / total
        score = max(0, int((1.0 - ratio) * 100))
        
        # ⭐⭐ AHORA SÍ HACER EL DEBUG CON LOS VALORES CALCULADOS ⭐⭐
        # print(f"[SCORE DEBUG] Ventana: {w:.1f}s | Total tiempo: {total:.1f}s | Distracciones: {distractor:.1f}s | Ratio: {ratio:.3f} | Score: {score}%")
        
        return score
    

    # ------------------ utilitarios ------------------
    def clear_history(self):
        """Borra todo el historial."""
        self.history.clear()

    def export_history_csv(self, path: str):
        """Exporta history a CSV (start, end, proc, title, seconds, class)"""
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["start_ts", "end_ts", "proc", "title", "seconds", "class"])
                for start_ts, end_ts, proc, title, seconds in list(self.history):
                    cls = self._classify_event(start_ts, end_ts, proc, title, seconds)
                    writer.writerow([start_ts, end_ts, proc, title, seconds, cls])
            return True
        except Exception as e:
            print("[FocusScorer] export error:", e)
            return False

    # ajustes en runtime
    def add_productive(self, keyword: str):
        self.productive.append(keyword.lower())

    def remove_productive(self, keyword: str):
        self.productive = [k for k in self.productive if k != keyword.lower()]

    def add_distractor(self, keyword: str):
        self.distractors.append(keyword.lower())

    def remove_distractor(self, keyword: str):
        self.distractors = [k for k in self.distractors if k != keyword.lower()]

    def set_window_seconds(self, seconds: int):
        self.window_seconds = int(seconds)
        self._prune_old()

    def set_distractor_threshold_seconds(self, seconds: int):
        self.distractor_threshold_seconds = int(seconds)
