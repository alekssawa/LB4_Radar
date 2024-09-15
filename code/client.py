import asyncio
import websockets
import json

# Переменная для хранения кэшированных данных
cached_data = None

async def connect():
    global cached_data
    uri = "ws://localhost:4000"
    try:
        async with websockets.connect(uri) as websocket:
            print("Підключено до WebSocket сервера")

            # Обрабатываем сообщения от сервера
            async for message in websocket:
                data = json.loads(message)
                if 'echoResponses' in data and data['echoResponses'] != []:
                    data['distance'] = round(300_000 * data['echoResponses'][0]['time'] / 2, 2)
                    print(f"client:{data}")
                    cached_data = data  # Сохраняем данные в кэш
    except websockets.exceptions.ConnectionClosed as e:
        print(f"З'єднання закрито: {e.reason}")
    except Exception as e:
        print(f"Помилка WebSocket: {e}")

async def get_data():
    global cached_data
    # Возвращаем кэшированные данные
    return cached_data
