#app.py
from flask import Flask, render_template, jsonify, request
import requests
from flask_cors import CORS
import websockets
import logging
import asyncio
import plotly.graph_objects as go
from client import get_data, connect, send_config_to_websocket
import json

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для всех доменов и методов

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Создаем отдельную задачу для подключения к WebSocket, если еще не создана
async def start_websocket_connection():
    if not getattr(start_websocket_connection, "started", False):
        await connect()
        start_websocket_connection.started = True

# Запускаем цикл событий при запуске приложения
def start_event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(start_websocket_connection())
    loop.run_forever()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/graph-data')
def graph_data():
    data = asyncio.run(get_data())
    if data:
        distance = data.get('distance', 0)
        scanAngle = data.get('scanAngle', 0)

        fig = go.Figure(data=go.Scatterpolar(
            r=[distance],
            theta=[scanAngle],
            mode='markers',
        ))

        fig.update_layout(showlegend=False, polar=dict(radialaxis=dict(range=[0, 200])))

        graphJSON = fig.to_json()
        return jsonify(graphJSON)
    else:
        return jsonify({"error": "Нет данных"})


@app.route('/send-config', methods=['POST'])
def send_config():
    # Получаем данные из запроса
    data = request.json

    # URL целевого сервера
    url = "http://localhost:4000/config"

    # Отправка PUT-запроса на целевой сервер
    response = requests.put(url, headers={"Content-Type": "application/json"}, data=json.dumps(data))

    # Возвращаем ответ от целевого сервера
    return jsonify({
        "status_code": response.status_code,
        "response": response.text
    })

if __name__ == "__main__":
    import threading
    event_loop_thread = threading.Thread(target=start_event_loop)
    event_loop_thread.start()

    app.run(debug=True)
