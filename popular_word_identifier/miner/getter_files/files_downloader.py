import urllib.request
import json
import os

class FileDownloader:
    def __init__(self, storage_path="../../temp_data"):
        self.storage_path = storage_path
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)

    def get_repo_files(self, repo_url, token=None):
        parts = repo_url.rstrip('/').split('/')
        owner, repo_name = parts[-2], parts[-1]
        
        # 1. Obtener el árbol de archivos
        # La opción recursive=1 para obtener todos los archivos en los directorios
        tree_url = f"https://api.github.com/repos/{owner}/{repo_name}/git/trees/main?recursive=1"
        
        data = self._fetch_api(tree_url, token)
        
        if data is None:
            tree_url = tree_url.replace('/main?', '/master?')
            data = self._fetch_api(tree_url, token)

        if not data or 'tree' not in data:
            print(f"   [!] No se pudo acceder al árbol de {repo_name}")
            return []

        downloaded_paths = []

        # 2. Filtrar y descargar
        for file_info in data['tree']:
            path = file_info['path']
            if path.endswith('.py') or path.endswith('.java'):
                branch = "main" if "main" in tree_url else "master"
                raw_url = f"https://raw.githubusercontent.com/{owner}/{repo_name}/{branch}/{path}"
                
                local_filename = self._save_file(raw_url, path, repo_name)
                if local_filename:
                    downloaded_paths.append(local_filename)
        
        return downloaded_paths

    def _save_file(self, url, original_path, repo_name):
        try:
            # se crea un nombre único para evitar colisiones y no crear la estructura de directorios del repositorio
            safe_name = original_path.replace('/', '_')
            full_path = os.path.join(self.storage_path, f"{repo_name}_{safe_name}")
            
            with urllib.request.urlopen(url) as response:
                with open(full_path, 'wb') as out_file:
                    out_file.write(response.read())
            return full_path
        except:
            return None

    def _fetch_api(self, url, token):
        headers = {"User-Agent": "Miner-Visualizador-App"}
        if token: headers["Authorization"] = f"token {token}"
        
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode())
        except:
            return None

    def clean_file(self, file_path):
        if os.path.exists(file_path):
            os.remove(file_path)