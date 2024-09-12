import asyncio
import websockets
import json

async def connect():
    uri = "ws://localhost:4000"
    try:
        async with websockets.connect(uri) as websocket:
            #print("Підключено до WebSocket сервера")

            # Обрабатываем сообщения от сервера
            async for message in websocket:
                data = json.loads(message)
                #print(f"Отримані дані: {message}")
                if 'echoResponses' in data and data['echoResponses'] != []:
                    data['distance'] = round(300_000 * data['echoResponses'][0]['time']/2, 2)
                    print(data)
                    #return data
                # Здесь можно добавить обработку данных и отображение на графике

    except websockets.exceptions.ConnectionClosed as e:
        print(f"З'єднання закрито: {e.reason}")

    except Exception as e:
        print(f"Помилка WebSocket: {e}")


# Запускаем асинхронный цикл для подключения
asyncio.get_event_loop().run_until_complete(connect())