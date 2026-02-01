import requests

def test_socks5_proxy():
    proxy_url = "socks5://494300202:5hrIZjjYavY4ZmOQlKIm@176.9.113.112:48001"
    
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }
    
    try:
        print("Тестируем SOCKS5 прокси...")
        
        # Тест IP
        response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=15)
        print(f"IP через прокси: {response.json()}")
        
        # Тест HTTPS
        response = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=15)
        print(f"HTTPS работает: {response.json()}")
        
        print("SOCKS5 прокси работает!")
        return True
        
    except Exception as e:
        print(f"Ошибка SOCKS5: {e}")
        return False

if __name__ == "__main__":
    test_socks5_proxy()