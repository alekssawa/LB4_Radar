from flask import Flask, render_template, jsonify, request
import websockets
import logging
import asyncio
import plotly.graph_objects as go
from client import get_data, connect

app = Flask(__name__)

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

@app.route('/config', methods=['PUT'])
def update_config():
    try:
        data = request.get_json()
        measurements_per_rotation = data.get('measurementsPerRotation')
        rotation_speed = data.get('rotationSpeed')
        target_speed = data.get('targetSpeed')

        if measurements_per_rotation is None or rotation_speed is None or target_speed is None:
            return jsonify({"error": "Недостаточно данных"}), 400

        # Форматируем данные для отправки через WebSocket
        ws_data = {
            "measurementsPerRotation": measurements_per_rotation,
            "rotationSpeed": rotation_speed,
            "targetSpeed": target_speed
        }

        # Отправляем данные на WebSocket сервер
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(send_config_to_websocket(str(ws_data)))
        loop.close()

        return jsonify({"response": response}), 200

    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "Произошла ошибка на сервере"}), 500

if __name__ == "__main__":
    import threading
    event_loop_thread = threading.Thread(target=start_event_loop)
    event_loop_thread.start()

    app.run(debug=True)
