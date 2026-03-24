FROM python:3.10-slim

WORKDIR /app

# Se copian las dependencias utilizadas por el miner
COPY dependencies.txt ./miner/dependencies.txt

RUN pip install --no-cache-dir -r ./miner/dependencies.txt

COPY . ./miner/

# Se establece PYTHONPATH al directorio raíz para la ejecución de 'import miner...'
ENV PYTHONPATH="/app"

CMD ["python", "-m", "miner.controller.miner_controller"]
