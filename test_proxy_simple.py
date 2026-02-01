import requests

def test_proxy_simple():
    """Простой тест HTTP прокси"""
    
    proxy_url = "http://494300202:5hrIZjjYavY4ZmOQlKIm@176.9.113.112:48000"
    
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }
    
    try:
        print("Тестируем прокси...")
        print(f"Прокси: {proxy_url}")
        
        # Проверяем IP
        response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=10)
        print(f"✅ IP через прокси: {response.json()}")
        
        # Проверяем доступность Avito
        response = requests.get('https://m.avito.ru', proxies=proxies, timeout=10)
        print(f"✅ Avito доступен: {response.status_code}")
        
        print("✅ Прокси работает!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_proxy_simple()