#Задание 1.
В файле Тестовое1.txt

# Тестирование микросервиса объявлений Avito

## Описание
Автоматизированные тесты для проверки API микросервиса объявлений. 
Покрывает 6 эндпоинтов:
1. Создание объявления (POST /api/1/item)
2. Получение объявления по ID (GET /api/1/item/{id})
3. Получение всех объявлений продавца (GET /api/1/{sellerID}/item)
4. Получение статистики v1 (GET /api/1/statistic/{id})
5. Получение статистики v2 (GET /api/2/statistic/{id})
6. Удаление объявления (DELETE /api/2/item/{id})

## Требования
- Python 3.7+
- Библиотеки: pytest, requests

## Установка
```bash
pip install pytest requests
```

## Запуск тестов
```bash
pytest -v test_avito_api.py
``` 

## Генерация отчёта
```bash
pytest --junitxml=report.xml test_avito_api.py
```
