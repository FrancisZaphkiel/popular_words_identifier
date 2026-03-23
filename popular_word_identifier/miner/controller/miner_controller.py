from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import threading
import queue
import json
import time
from dotenv import load_dotenv

from getter_repo.repo_finder import RepoMiner
from getter_files.files_downloader import FileDownloader
from parser.getter_names import NameExtractor
from convert.word_splitter import WordSplitter

app = Flask(__name__)
CORS(app)

# El queue pasa las palabras del hilo minero al hilo del servidor web de forma segura
word_queue = queue.Queue()
miner_thread = None

miner = RepoMiner()
downloader = FileDownloader()
extractor = NameExtractor()
splitter = WordSplitter()

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def mining_pipeline(language, token):
    miner.is_running = True
    miner.current_page = 1
    miner.last_star_count = 1000000

    print(f"[*] Iniciando pipeline de minería para: {language}")

    while miner.is_running:
        query = f"language:{language}+stars:<{miner.last_star_count}"
        url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page=10&page={miner.current_page}"
        
        repos_data = miner._fetch(url, token)
        
        if not repos_data or 'items' not in repos_data:
            print("[!] Error o límite de API alcanzado. Esperando...")
            time.sleep(10)
            continue

        for repo in repos_data['items']:
            if not miner.is_running: 
                break
            
            repo_url = repo['html_url']
            print(f"-> Procesando repo: {repo_url}")
            
            downloader.get_repo_files(repo_url, token)
            
            raw_names = extractor.extract_from_storage()
            
            natural_words = splitter.split_to_natural_language(raw_names)
            
            if natural_words:
                word_queue.put(natural_words)
            
            miner.last_star_count = repo['stargazers_count']

        miner.current_page += 1
        if miner.current_page > 10:
            miner.current_page = 1
        
        time.sleep(2)

    print("[*] Pipeline de minería detenido.")

# --- ENDPOINTS REST ---

@app.route('/miner/start', methods=['POST'])
def start_mining():
    global miner_thread
    data = request.json
    language = data.get('language', 'python')
    
    if miner.is_running:
        return jsonify({"status": "error", "message": "El minero ya está en ejecución."}), 400

    miner_thread = threading.Thread(target=mining_pipeline, args=(language, GITHUB_TOKEN))
    miner_thread.daemon = True
    miner_thread.start()
    
    return jsonify({"status": "success", "message": f"Minería iniciada para {language}"})

@app.route('/miner/stop', methods=['POST'])
def stop_mining():
    miner.stop()
    return jsonify({"status": "success", "message": "Señal de detención enviada al minero."})

# --- ENDPOINT SSE (Server-Sent Events) ---

@app.route('/miner/stream')
def stream_words():
    def event_stream():
        while True:
            words = word_queue.get() 
            
            yield f"data: {json.dumps({'words': words})}\n\n"
            
            word_queue.task_done()

    return Response(event_stream(), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)