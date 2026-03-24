from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import threading
import queue
import json
import time
import os
from dotenv import load_dotenv

from miner.getter_repo.repo_finder import RepoMiner
from miner.getter_files.files_downloader import FileDownloader
from miner.parser.name_extractor import NameExtractor
from miner.convert.word_splitter import WordSplitter

app = Flask(__name__)
CORS(app)

# El queue pasa las palabras del hilo minero al hilo del servidor web de forma segura
word_queue = queue.Queue()
active_miners = []
mining_threads = []
is_globally_running = False

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def mining_pipeline(language, token):
    miner = RepoMiner()
    downloader = FileDownloader()
    extractor = NameExtractor()
    splitter = WordSplitter()
    
    active_miners.append(miner)

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
    global is_globally_running, active_miners, mining_threads
    
    if is_globally_running:
        return jsonify({"status": "error", "message": "El minero ya está en ejecución."}), 400

    is_globally_running = True
    active_miners.clear()
    mining_threads.clear()

    for lang in ['python', 'java']:
        t = threading.Thread(target=mining_pipeline, args=(lang, GITHUB_TOKEN))
        t.daemon = True
        t.start()
        mining_threads.append(t)
    
    return jsonify({"status": "success", "message": "Minería concurrente iniciada para python y java"})

@app.route('/miner/stop', methods=['POST'])
def stop_mining():
    global is_globally_running
    for miner in active_miners:
        miner.stop()
    is_globally_running = False
    return jsonify({"status": "success", "message": "Señal de detención enviada a los mineros."})

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
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True, use_reloader=False)