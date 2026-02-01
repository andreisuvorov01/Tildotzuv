#!/usr/bin/env python3
"""
Пример использования API для парсинга zakupki.gov.ru
"""

import requests
import json


def test_api_with_zakupki():
    """Тестирует API с URL zakupki.gov.ru"""
    
    # URL для тестирования
    test_url = "https://zakupki.gov.ru/epz/order/extendedsearch/results.html?morphology=on&search-filter=Дате+размещения&pageNumber=1&sortDirection=false&recordsPerPage=_10&showLotsInfoHidden=false&sortBy=UPDATE_DATE&fz44=on&fz223=on&af=on&currencyIdGeneral=-1"
    
    # Данные для отправки
    payload = {
        "url": test_url
    }
    
    # URL API (предполагаем, что сервер запущен на localhost:8000)
    api_url = "http://localhost:8000/api/v1/extract-reviews"
    
    try:
        print("Отправляем запрос к API...")
        print(f"URL для парсинга: {test_url}")
        
        response = requests.post(api_url, json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\nУспешно получен ответ!")
            print(f"Источник: {data['source_url']}")
            print(f"Количество найденных закупок: {data['reviews_count']}")
            
            print("\nПервые 3 закупки:")
            for i, review in enumerate(data['reviews'][:3], 1):
                print(f"\n--- Закупка {i} ---")
                print(f"Описание: {review['text'][:100]}...")
                print(f"Заказчик: {review['author']}")
                print(f"Цена: {review['rating']}")
                
        else:
            print(f"Ошибка API: {response.status_code}")
            print(f"Ответ: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Ошибка: Не удается подключиться к API. Убедитесь, что сервер запущен на localhost:8000")
    except requests.exceptions.Timeout:
        print("Ошибка: Превышено время ожидания ответа от API")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")


if __name__ == "__main__":
    print("=== Тест API для zakupki.gov.ru ===")
    test_api_with_zakupki()