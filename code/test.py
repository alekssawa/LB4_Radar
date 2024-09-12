import json

# Пример данных
data = {
    'pulseDuration': 1,
    'scanAngle': 236,
    'echoResponses': [{'time': 0.0006196959152395295, 'power': 0.0533237188393241}],
    'distance': 92.95
}

# Проверяем сериализацию данных
try:
    json_string = json.dumps(data)
    print("JSON сериализация успешна:", json_string)
except TypeError as e:
    print("Ошибка сериализации JSON:", e)