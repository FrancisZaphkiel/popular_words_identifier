import time
import urllib.request
import json

class RepoMiner:
    def __init__(self):
        self.is_running = False
        self.last_star_count = 1000000
        self.current_page = 1

    def start_mining(self, language, token=None):
        self.is_running = True
        print(f"--- Iniciando Minería Infinita de {language} ---")

        while self.is_running:
            query = f"language:{language}+stars:<{self.last_star_count}"
            url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page=100&page={self.current_page}"
            
            print(f"Extrayendo página {self.current_page} (Estrellas < {self.last_star_count})...")
            
            repos_data = self._fetch(url, token)
            
            if not repos_data or 'items' not in repos_data or len(repos_data['items']) == 0:
                print("No hay más repositorios o error de conexión.")
                break

            # 1. Enviar URLs al componente getter_files
            for repo in repos_data['items']:
                if not self.is_running: break
                print(f"Procesando: {repo['html_url']}")
                self.last_star_count = repo['stargazers_count']

            # 2. Manejo de paginación
            self.current_page += 1
            if self.current_page > 10:
                self.current_page = 1
            time.sleep(2)

        print("--- Proceso detenido por el usuario o fin de datos ---")

    def stop(self):
        self.is_running = False

    def _fetch(self, url, token):
        headers = {"User-Agent": "Miner-Visualizador-App"}
        if token:
            headers["Authorization"] = f"token {token}"
            
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f"Error HTTP en _fetch: {e}")
            return None