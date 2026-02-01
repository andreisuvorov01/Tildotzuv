import requests

def test_proxy():
    proxy_url = "http://494300202:5hrIZjjYavY4ZmOQlKIm@176.9.113.112:48000"
    
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }
    
    try:
        print("Тестируем прокси...")
        
        # Тест 1: Проверка IP
        response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=10)
        print(f"✅ IP через прокси: {response.json()}")
        
        # Тест 2: Проверка HTTPS
        response = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=10)
        print(f"✅ HTTPS работает: {response.json()}")
        
        # Тест 3: Проверка zakupki.gov.ru
        response = requests.get('https://zakupki.gov.ru', proxies=proxies, timeout=15)
        print(f"✅ zakupki.gov.ru доступен: {response.status_code}")
        
        print("✅ Прокси работает корректно!")
        return True
        
    except requests.exceptions.ProxyError as e:
        print(f"❌ Ошибка прокси: {e}")
        return False
    except requests.exceptions.Timeout as e:
        print(f"❌ Таймаут: {e}")
        return False
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        return False

if __name__ == "__main__":
    test_proxy()