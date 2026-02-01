#!/usr/bin/env python3
"""
Тест сетевых настроек в Docker контейнере
"""
import asyncio
import subprocess
import sys

async def test_network():
    """Тестирует сеть в Docker контейнере"""

    print("=== Docker Network Diagnostics ===\n")

    # Тест 1: Проверка DNS
    print("1. Testing DNS resolution...")
    try:
        result = subprocess.run(['nslookup', 'zakupki.gov.ru'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ DNS resolution successful")
            print(f"   Output: {result.stdout.split('Address:')[1].strip() if 'Address:' in result.stdout else 'OK'}")
        else:
            print(f"❌ DNS resolution failed: {result.stderr}")
    except Exception as e:
        print(f"❌ DNS test error: {e}")

    # Тест 2: Проверка ping
    print("\n2. Testing ping to google.com...")
    try:
        result = subprocess.run(['ping', '-c', '3', 'google.com'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Ping successful")
        else:
            print(f"❌ Ping failed: {result.stderr}")
    except Exception as e:
        print(f"❌ Ping test error: {e}")

    # Тест 3: Проверка curl
    print("\n3. Testing HTTP access to zakupki.gov.ru...")
    try:
        result = subprocess.run(['curl', '-I', '--max-time', '10', 'https://zakupki.gov.ru'],
                              capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            print("✅ HTTP access successful")
            status_line = [line for line in result.stdout.split('\n') if line.startswith('HTTP/')]
            if status_line:
                print(f"   Status: {status_line[0]}")
        else:
            print(f"❌ HTTP access failed: {result.stderr}")
    except Exception as e:
        print(f"❌ HTTP test error: {e}")

    # Тест 4: Проверка DNS серверов
    print("\n4. Testing DNS servers...")
    dns_servers = ['8.8.8.8', '1.1.1.1', '77.88.8.8']
    for dns in dns_servers:
        try:
            result = subprocess.run(['dig', '@' + dns, 'zakupki.gov.ru'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and 'ANSWER SECTION' in result.stdout:
                print(f"✅ DNS {dns} works")
                break
            else:
                print(f"❌ DNS {dns} failed")
        except Exception as e:
            print(f"❌ DNS {dns} error: {e}")

    print("\n=== Network Diagnostics Complete ===")

if __name__ == "__main__":
    asyncio.run(test_network())
