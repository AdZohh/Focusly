# src/core/audio_manager.py
import os
import pygame
import time

AUDIO_EXTS = (".wav", ".mp3", ".ogg", ".flac")

class AudioManager:
    """
    AudioManager que detecta categorías basadas en subcarpetas dentro de assets/sounds
    - get_categories(): lista de categorías
    - get_tracks(category): lista de archivos (filenames) dentro de la carpeta de la categoría
    - play_track(category, index_or_name): reproduce la pista seleccionada
    """

    def __init__(self, assets_root=None):
        self._ensure_mixer_init()

        # default: project_root/assets or project_root/assets/sounds
        if assets_root is None:
            assets_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets"))
        # preferir assets/sounds si existe
        if os.path.isdir(os.path.join(assets_root, "sounds")):
            assets_root = os.path.join(assets_root, "sounds")
        self.assets_root = assets_root
        print(f"[AudioManager] assets_root -> {self.assets_root}")

        # Construir mapping category -> absolute folder path (detectando subfolders)
        self._category_dirs = {}
        if os.path.isdir(self.assets_root):
            for entry in sorted(os.listdir(self.assets_root)):
                p = os.path.join(self.assets_root, entry)
                if os.path.isdir(p):
                    # normalizar nombre visible de categoría:
                    display_name = entry
                    # reglas pequeñas: querer 'Dreamscapes' en vez de 'Dreamscape' etc.
                    if entry.lower().startswith("dream"):
                        display_name = "Dreamscapes"
                    elif "rain" in entry.lower():
                        display_name = "Rain"
                    elif entry.lower().startswith("deep"):
                        display_name = "Deep Focus"
                    # si ya existe display_name, añadir sufijo
                    base = display_name
                    i = 1
                    while display_name in self._category_dirs:
                        display_name = f"{base} {i}"
                        i += 1
                    self._category_dirs[display_name] = p
        else:
            print("[AudioManager] WARNING: assets root not found:", self.assets_root)

        # estado de reproducción
        self.current_category = None
        self.current_track_filename = None
        self._paused = False
        self._is_playing = False
        self._volume = 0.7
        try:
            pygame.mixer.music.set_volume(self._volume)
        except Exception:
            pass

    def _ensure_mixer_init(self):
        try:
            if not pygame.get_init():
                pygame.init()
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            print("[AudioManager] pygame mixer initialized")
        except Exception as e:
            print("[AudioManager] Error init mixer:", e)

    # ------------- helpers -------------
    def get_categories(self):
        """Devuelve la lista visible de categorías detectadas (ordenada)."""
        return list(self._category_dirs.keys())

    def _category_path(self, category):
        return self._category_dirs.get(category)

    def _list_files_in_dir(self, folder):
        if not folder or not os.path.isdir(folder):
            return []
        files = []
        for fn in sorted(os.listdir(folder)):
            if fn.lower().endswith(AUDIO_EXTS):
                files.append(fn)
        return files

    def get_tracks(self, category):
        """Devuelve lista de filenames (relativos) para esa categoría (filtrados por extensión)."""
        folder = self._category_path(category)
        return self._list_files_in_dir(folder)

    def _candidate_path(self, filename, category):
        folder = self._category_path(category)
        if not folder:
            return None
        return os.path.join(folder, filename) if not os.path.isabs(filename) else filename

    # ------------- reproducción -------------
    def play_track(self, category, index_or_name, loop=True):
        tracks = self.get_tracks(category)
        if not tracks:
            print(f"[AudioManager] no tracks available for category '{category}'")
            return

        # resolver filename
        if isinstance(index_or_name, int):
            if index_or_name < 0 or index_or_name >= len(tracks):
                print("[AudioManager] invalid track index", index_or_name)
                return
            filename = tracks[index_or_name]
        else:
            filename = str(index_or_name)
            if filename not in tracks:
                print("[AudioManager] requested track not in available tracks:", filename)
                return

        path = self._candidate_path(filename, category)
        exists = os.path.exists(path) if path else False
        print(f"[AudioManager] play_track -> category='{category}', filename='{filename}', path='{path}', exists={exists}")
        if not exists:
            return

        if self.current_category == category and self.current_track_filename == filename:
            # mismo track
            if self._paused:
                try:
                    pygame.mixer.music.unpause()
                    self._paused = False
                    self._is_playing = True
                    print("[AudioManager] resumed same track")
                except Exception as e:
                    print("[AudioManager] unpause error:", e)
            else:
                print("[AudioManager] same track already playing -> noop")
            return

        # nuevo track: load & play
        try:
            pygame.mixer.music.load(path)
            if loop:
                pygame.mixer.music.play(-1)
            else:
                pygame.mixer.music.play()
            pygame.mixer.music.set_volume(self._volume)
            self.current_category = category
            self.current_track_filename = filename
            self._paused = False
            self._is_playing = True
            time.sleep(0.01)
            print("[AudioManager] playing:", path)
        except Exception as e:
            print("[AudioManager] error al cargar/reproducir:", e)

    def pause_all(self):
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
                self._paused = True
                self._is_playing = False
                print("[AudioManager] paused")
        except Exception as e:
            print("[AudioManager] pause error:", e)

    def resume_all(self):
        try:
            if self._paused:
                pygame.mixer.music.unpause()
                self._paused = False
                self._is_playing = True
                print("[AudioManager] resumed")
        except Exception as e:
            print("[AudioManager] resume error:", e)

    def stop_all(self):
        try:
            pygame.mixer.music.stop()
            print("[AudioManager] stopped")
        except Exception:
            pass
        self.current_category = None
        self.current_track_filename = None
        self._paused = False
        self._is_playing = False

    def set_master_volume(self, v: float):
        try:
            v = max(0.0, min(1.0, float(v)))
            pygame.mixer.music.set_volume(v)
            self._volume = v
            print("[AudioManager] volume set to", v)
        except Exception as e:
            print("[AudioManager] set volume error:", e)

    def is_playing(self):
        try:
            return self._is_playing and pygame.mixer.music.get_busy()
        except Exception:
            return False

    def is_paused(self):
        return self._paused

