#!/usr/bin/env python3
"""
Тест API с фильтрами для zakupki.gov.ru
"""

import requests
import json


def test_api_with_filters():
    """Тестирует API с различными фильтрами"""
    
    api_url = "http://localhost:8000/api/v1/extract-reviews"
    base_url = "https://zakupki.gov.ru/epz/order/extendedsearch/results.html"
    
    test_cases = [
        {
            "name": "Базовый запрос без фильтров",
            "payload": {
                "url": base_url
            }
        },
        {
            "name": "Поиск медицинского оборудования",
            "payload": {
                "url": base_url,
                "filters": {
                    "search_text": "медицинское оборудование",
                    "records_per_page": 20
                }
            }
        },
        {
            "name": "Только 44-ФЗ, сортировка по цене",
            "payload": {
                "url": base_url,
                "filters": {
                    "sort_by": "PRICE",
                    "ascending": False,
                    "law_types": {
                        "fz44": True,
                        "fz223": False,
                        "af": False
                    }
                }
            }
        },
        {
            "name": "Фильтр по цене и дате",
            "payload": {
                "url": base_url,
                "filters": {
                    "price_range": {
                        "min": 100000,
                        "max": 1000000
                    },
                    "date_range": {
                        "from": "01.01.2026",
                        "to": "31.01.2026"
                    }
                }
            }
        },
        {
            "name": "Комплексный фильтр",
            "payload": {
                "url": base_url,
                "filters": {
                    "search_text": "строительство",
                    "sort_by": "PRICE",
                    "ascending": True,
                    "page": 1,
                    "records_per_page": 10,
                    "law_types": {
                        "fz44": True,
                        "fz223": True,
                        "af": False
                    },
                    "price_range": {
                        "min": 500000,
                        "max": 5000000
                    }
                }
            }
        }
    ]
    
    print("=== Тест API с фильтрами ===\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['name']}")
        
        try:
            response = requests.post(api_url, json=test_case['payload'], timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Статус: OK")
                print(f"   URL: {data['source_url']}")
                print(f"   Найдено закупок: {data['reviews_count']}")
                
                if data.get('applied_filters'):
                    print(f"   Применены фильтры: {len(data['applied_filters'])} параметров")
                
                if data['reviews']:
                    print(f"   Первая закупка: {data['reviews'][0]['text'][:50]}...")
                    
            else:
                print(f"   Ошибка: {response.status_code}")
                print(f"   Ответ: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("   Ошибка: API недоступен (сервер не запущен)")
        except requests.exceptions.Timeout:
            print("   Ошибка: Превышено время ожидания")
        except Exception as e:
            print(f"   Ошибка: {e}")
            
        print()


def test_filter_url_generation():
    """Тестирует генерацию URL с фильтрами"""
    
    print("=== Тест генерации URL ===\n")
    
    # Имитируем запрос с фильтрами
    filters = {
        "search_text": "компьютеры",
        "sort_by": "PRICE", 
        "ascending": False,
        "page": 2,
        "records_per_page": 50,
        "law_types": {
            "fz44": True,
            "fz223": False,
            "af": False
        },
        "price_range": {
            "min": 50000,
            "max": 500000
        }
    }
    
    # Создаем парсер и генерируем URL
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from app.services.parsers.zakupki import ZakupkiParser
    
    parser = ZakupkiParser()
    generated_url = parser.create_filtered_url(**filters)
    
    print("Сгенерированный URL:")
    print(generated_url)
    print()
    
    # Разбираем URL обратно
    from app.services.zakupki_filters import ZakupkiFilters
    parsed_filters = ZakupkiFilters.from_url(generated_url)
    
    print("Извлеченные параметры:")
    for key, value in parsed_filters.get_filters_dict().items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    print("Тестирование API с фильтрами zakupki.gov.ru\n")
    
    # Тест генерации URL (работает без сервера)
    test_filter_url_generation()
    
    print("\n" + "="*50)
    print("Для тестирования API запустите сервер:")
    print("python app/main.py")
    print("="*50 + "\n")
    
    # Тест API (требует запущенный сервер)
    test_api_with_filters()