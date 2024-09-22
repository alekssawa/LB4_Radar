import requests
import json

# Конфигурация для отправки
config = {
    "measurementsPerRotation": 360,
    "rotationSpeed": 60,
    "targetSpeed": 100
}

# URL сервера
url = "http://localhost:4000/config"

# Отправка PUT-запроса
response = requests.put(url, headers={"Content-Type": "application/json"})

# Вывод ответа от сервера
print(f"Статус-код: {response.status_code}")
print(f"Ответ от сервера: {response.text}")
