#!/usr/bin/env python3
"""
Тестовый скрипт для проверки парсера zakupki.gov.ru
"""

import asyncio
import sys
import os

# Добавляем корневую папку проекта в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.parsers.zakupki import ZakupkiParser


async def test_zakupki_parser():
    """Тестирует парсер на локальном HTML файле"""
    
    # Путь к файлу с примером HTML
    html_file_path = "Закупки.htm"
    
    try:
        # Читаем HTML файл
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        print(f"HTML файл загружен, размер: {len(html_content)} символов")
        
        # Создаем парсер
        parser = ZakupkiParser()
        
        # Парсим содержимое
        url = "https://zakupki.gov.ru/epz/order/extendedsearch/results.html"
        results = parser.parse(html_content, url)
        
        print(f"\nНайдено закупок: {len(results)}")
        
        # Выводим первые 3 результата
        for i, item in enumerate(results[:3], 1):
            print(f"\n--- Закупка {i} ---")
            print(f"Описание: {item.text[:100]}...")
            print(f"Заказчик: {item.author}")
            print(f"Цена: {item.rating}")
        
        return True
        
    except FileNotFoundError:
        print(f"Файл {html_file_path} не найден")
        return False
    except Exception as e:
        print(f"Ошибка: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_zakupki_parser())
    if success:
        print("\nТест парсера zakupki.gov.ru прошел успешно!")
    else:
        print("\nТест парсера zakupki.gov.ru провалился!")