// --- CONFIGURACIÓN Y ESTADO GLOBAL ---
const API_BASE_URL = 'http://localhost:5000/miner';
let wordFrequencies = {};
let eventSource = null;
let chart = null;

const inputTopN = document.getElementById('topN');
const btnStart = document.getElementById('btnStart');
const btnStop = document.getElementById('btnStop');
const ctx = document.getElementById('wordChart').getContext('2d');

function initChart() {
    const chartColor = '#10b981';
    const gridColor = '#374151';
    const textColor = '#9e9e9e';

    chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Frecuencia de Aparición',
                data: [],
                backgroundColor: chartColor,
                borderColor: chartColor,
                borderWidth: 1,
                borderRadius: 5,
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
            },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: { color: gridColor },
                    ticks: { color: textColor }
                },
                y: {
                    grid: { display: false },
                    ticks: { color: textColor, font: { weight: 'bold' } }
                }
            },
            animation: {
                duration: 400
            }
        }
    });
}

function processIncomingWords(wordsArray) {
    wordsArray.forEach(word => {
        wordFrequencies[word] = (wordFrequencies[word] || 0) + 1;
    });

    updateChartData();
}

function updateChartData() {
    const N = Number.parseInt(inputTopN.value) || 10;
    const sortedEntries = Object.entries(wordFrequencies)
        .sort((a, b) => b[1] - a[1])
        .slice(0, N);

    const labels = sortedEntries.map(entry => entry[0]);
    const data = sortedEntries.map(entry => entry[1]);

    chart.data.labels = labels;
    chart.data.datasets[0].data = data;

    const newHeight = Math.max(400, N * 40);
    chart.canvas.parentNode.style.height = `${newHeight}px`;

    chart.update();
}

async function startMining() {
    const topNValue = Number.parseInt(inputTopN.value) || 10;
    const language = 'python';

    try {
        const response = await fetch(`${API_BASE_URL}/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ language: language, topN: topNValue })
        });

        const result = await response.json();

        if (result.status === 'success') {
            console.log("Miner iniciado correctamente.");
            wordFrequencies = {};
            updateChartData();
            connectStream();
            updateUiState(true);
        } else {
            alert(`Error del Miner: ${result.message}`);
        }

    } catch (error) {
        console.error("Error de conexión:", error);
        alert("No se pudo conectar con el servidor Miner. Asegúrate de que esté corriendo en el puerto 5000.");
    }
}

async function stopMining() {
    try {
        await fetch(`${API_BASE_URL}/stop`, { method: 'POST' });

        if (eventSource) {
            eventSource.close();
            console.log("Conexión SSE cerrada.");
        }

        updateUiState(false);

    } catch (error) {
        console.error("Error al detener:", error);
    }
}

function connectStream() {
    if (eventSource) eventSource.close();

    eventSource = new EventSource(`${API_BASE_URL}/stream`);

    eventSource.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            if (data.words && data.words.length > 0) {
                processIncomingWords(data.words);
            }
        } catch (error) {
            console.error("Error convirtiendo datos de SSE:", error);
        }
    };

    eventSource.onerror = (error) => {
        console.error("Error en conexxión con SSE:", error);
    };
}

function updateUiState(isRunning) {
    if (isRunning) {
        btnStart.classList.add('running');
        btnStart.disabled = true;
        btnStart.innerText = "Obteniendo...";

        btnStop.classList.remove('inactive');
        btnStop.disabled = false;

        inputTopN.disabled = true;
    } else {
        btnStart.classList.remove('running');
        btnStart.disabled = false;
        btnStart.innerText = "Iniciar";

        btnStop.classList.add('inactive');
        btnStop.disabled = true;

        inputTopN.disabled = false;
    }
}

btnStart.addEventListener('click', startMining);
btnStop.addEventListener('click', stopMining);

inputTopN.addEventListener('keydown', (e) => {
    if (['e', 'E', '+', '-', '.'].includes(e.key)) {
        e.preventDefault();
    }
});

inputTopN.addEventListener('change', () => {
    if (Object.keys(wordFrequencies).length > 0) {
        updateChartData();
    }
});

initChart();