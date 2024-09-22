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

@app.route('/get-config', methods=['POST'])
def get_config():

    # URL целевого сервера
    url = "http://localhost:4000/config"

    # Отправка PUT-запроса на целевой сервер
    response = requests.put(url, headers={"Content-Type": "application/json"})

    if response.status_code == 200:
        response_data = response.json()

        config_data = response_data.get('config', {})  # Извлекаем данные конфигурации
        measurementsPerRotation = config_data.get('measurementsPerRotation', 0)
        rotationSpeed = config_data.get('rotationSpeed', 0)
        targetSpeed = config_data.get('targetSpeed', 0)
        return jsonify({
            "measurementsPerRotation": measurementsPerRotation,
            "rotationSpeed": rotationSpeed,
            "targetSpeed": targetSpeed
            #"config_data": config_data
        })
    else:
        return jsonify({
            "status_code": response.status_code,
            "error": "Не удалось получить данные"
        })
@app.route('/')
def index():
    response = requests.post('http://localhost:5000/get-config')

    if response.status_code == 200:
        json_data = response.json()  # Преобразуем ответ в JSON
    else:
        json_data = {"error": "Не удалось получить конфигурацию"}

    return render_template('index.html', json_data=json_data)
    #return render_template('index.html')

@app.route('/graph-data')
def graph_data():
    data = asyncio.run(get_data())
    if data:
        distance = data.get('distance', 0)
        scanAngle = data.get('scanAngle', 0)
        power = data.get('echoResponses', [{}])[0].get('power', 0)
        #print(power)
        if power >= 1000:
            power = 1000
        marker_color = 'blue' if power < 0.05 else 'red'
        marker_size = 10 + power / 10  # Размер точки
        marker_symbol = 'circle' if power < 0.05 else 'square'  # Форма точки

        hover_text = f"Distance: {distance}<br>Angle: {scanAngle}<br>Power: {power}"

        fig = go.Figure(data=go.Scatterpolar(
            r=[distance],
            theta=[scanAngle],
            mode='markers',
            marker=dict(
                color=marker_color,  # Цвет точки
                size=marker_size,  # Размер точки
                symbol=marker_symbol  # Форма точки
            ),
            hovertext=hover_text,  # Текст при наведении
            hoverinfo="text"  # Показываем только текст
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
    if response.status_code == 200:
        return jsonify({
            "status_code": response.status_code,
            "response": "Конфигурация обновлена",
            "updated_config": data  # Отправляем обновлённую конфигурацию
        })
    else:
        return jsonify({
            "status_code": response.status_code,
            "error": "Ошибка отправки конфигурации"
        })
    # Возвращаем ответ от целевого сервера
    # return jsonify({
    #     "status_code": response.status_code,
    #     "response": response.text
    # })



if __name__ == "__main__":
    import threading
    event_loop_thread = threading.Thread(target=start_event_loop)
    event_loop_thread.start()

    app.run(debug=True)
