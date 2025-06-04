import requests
import keyboard
import time

# IP do seu WLED
IP_WLED = "192.168.1.151"
URL_INFO  = f"http://{IP_WLED}/json/info"
URL_STATE = f"http://{IP_WLED}/json/state"

# 1) Descobre quantos LEDs a fita tem
resp = requests.get(URL_INFO, timeout=3)
resp.raise_for_status()
led_count = resp.json()["leds"]["count"]
print(f"LEDs detectados: {led_count}")

# índice do LED atualmente aceso
current = 0

def acende_apenas(i):
    """
    Divide a fita em até 3 segmentos:
     - segmento [0 .. i) apagado
     - segmento [i .. i+1) vermelho
     - segmento (i+1 .. fim] apagado
    e envia tudo num único POST.
    """
    segs = []
    # parte antes
    if i > 0:
        segs.append({
            "start": 0,
            "stop":  i,
            "col":   [[0,0,0]]
        })
    # o LED vermelho
    segs.append({
        "start": i,
        "stop":  i+1,
        "col":   [[255,0,0]]
    })
    # parte depois
    if i < led_count-1:
        segs.append({
            "start": i+1,
            "stop":  led_count,
            "col":   [[0,0,0]]
        })

    payload = {
        "on":  True,
        "seg": segs
    }
    # envia para o WLED
    requests.post(URL_STATE, json=payload, timeout=1)

# acende o LED 0 ao iniciar
acende_apenas(current)
print("Use ← e → para navegar. ESC para sair.")

# loop de leitura de teclas
while True:
    evento = keyboard.read_event()
    # só reagimos ao KEY_DOWN
    if evento.event_type != keyboard.KEY_DOWN:
        continue

    if evento.name == "right":
        current = (current + 1) % led_count
        acende_apenas(current)
    elif evento.name == "left":
        current = (current - 1) % led_count
        acende_apenas(current)
    elif evento.name == "esc":
        print("Encerrando...")
        break

    # pequena pausa pra não disparar múltiplos eventos seguidos
    time.sleep(0.05)
