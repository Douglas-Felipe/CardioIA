# =============================================================
# CardioIA - Fase 7 | Dispositivo de borda em MicroPython (ESP32)
# Autor: Douglas de Souza Felipe
#
# Migração do firmware C/C++ (Fase 3 - iot/src/main.cpp) para MicroPython.
#
# Sensores (Wokwi):
#   - DHT22 ........... temperatura corporal (°C) + umidade      -> GPIO15
#   - Potenciômetro 1 . frequência cardíaca simulada (30-180 bpm) -> GPIO34
#   - Potenciômetro 2 . SpO2 simulada (80-100 %)                 -> GPIO35
#   - Potenciômetro 3 . pressão arterial sistólica (80-200 mmHg) -> GPIO32
# Atuadores / feedback visual:
#   - OLED SSD1306 128x64 (I2C SDA=21, SCL=22)
#   - LED verde (GPIO26) = NORMAL | LED vermelho (GPIO27) = ATENÇÃO (pisca) / CRÍTICO (fixo)
#   - Buzzer (GPIO25) = bipa em CRÍTICO
#
# Fluxo: Sensor -> MicroPython (análise edge) -> HTTP POST -> Backend Python (Render)
#        -> ML/Multiagente (Fase 6) -> resposta exibida no OLED
#
# Comandos via Serial Monitor (teste de resiliência):
#   '0' -> simula desconexão (offline, leituras ficam no buffer local)
#   '1' -> reconecta e descarrega o buffer
# =============================================================

import gc
import sys
import time
import json
import select

import dht
import network
import urequests
from machine import ADC, I2C, PWM, Pin

import ssd1306

# ------------------------------------------------------------- Configuração
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASSWORD = ""
BACKEND_URL = "https://cardioia-backend.onrender.com"  # <- URL pública do Render
DEVICE_TOKEN = "cardioia-device-demo-token"            # <- mesmo valor de DEVICE_TOKEN no backend
DEVICE_ID = "cardioia-esp32-01"

READ_INTERVAL_MS = 5000      # período de leitura/envio
HTTP_TIMEOUT_S = 15          # Render free pode "acordar" lentamente
BUFFER_MAX = 20              # leituras guardadas quando offline

# ------------------------------------------------------------------ Hardware
dht_sensor = dht.DHT22(Pin(15))


def make_adc(pin):
    adc = ADC(Pin(pin))
    adc.atten(ADC.ATTN_11DB)  # faixa completa 0-3.3 V
    adc.width(ADC.WIDTH_12BIT)
    return adc


pot_bpm = make_adc(34)
pot_spo2 = make_adc(35)
pot_pa = make_adc(32)

led_green = Pin(26, Pin.OUT)
led_red = Pin(27, Pin.OUT)
buzzer = PWM(Pin(25), freq=2000, duty=0)

i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# ------------------------------------------------------------------- Estado
wlan = network.WLAN(network.STA_IF)
simulated_offline = False
offline_buffer = []
last_ai = {"classificacao_ml": "--", "probabilidade": None, "nivel": "--"}
blink_state = False

poller = select.poll()
poller.register(sys.stdin, select.POLLIN)


# ============================================================ Regras de borda
# Mesma lógica de backend/cardioia/vitals_rules.py (consistência edge <-> nuvem)
NORMAL, ATENCAO, CRITICO = "NORMAL", "ATENCAO", "CRITICO"
ORDER = {NORMAL: 0, ATENCAO: 1, CRITICO: 2}


def classify(bpm, spo2, temp, sys_bp):
    alerts = []
    level = NORMAL

    def bump(new_level, msg):
        nonlocal level
        alerts.append(msg)
        if ORDER[new_level] > ORDER[level]:
            level = new_level

    if bpm < 50 or bpm > 120:
        bump(CRITICO, "FC critica")
    elif bpm < 60 or bpm > 100:
        bump(ATENCAO, "FC alterada")

    if spo2 < 90:
        bump(CRITICO, "Hipoxemia")
    elif spo2 < 95:
        bump(ATENCAO, "SpO2 baixa")

    if temp >= 39.0 or temp < 35.0:
        bump(CRITICO, "Temp critica")
    elif temp >= 37.6:
        bump(ATENCAO, "Febre")

    if sys_bp >= 180 or sys_bp < 90:
        bump(CRITICO, "PA critica")
    elif sys_bp >= 140:
        bump(ATENCAO, "PA elevada")

    return level, alerts


# ================================================================ Leituras
def scale(adc, lo, hi):
    return lo + (adc.read() / 4095) * (hi - lo)


def read_sensors():
    try:
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        hum = dht_sensor.humidity()
    except OSError as e:
        print("[DHT22] Falha na leitura:", e)
        temp, hum = 36.5, None
    return {
        "bpm": round(scale(pot_bpm, 30, 180)),
        "spo2": round(scale(pot_spo2, 80, 100)),
        "temperature": round(temp, 1),
        "systolic": round(scale(pot_pa, 80, 200)),
        "humidity": hum,
    }


# ============================================================== Conectividade
def connect_wifi(timeout_s=15):
    if wlan.isconnected():
        return True
    wlan.active(True)
    print("[WiFi] Conectando a", WIFI_SSID, end="")
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    start = time.time()
    while not wlan.isconnected() and time.time() - start < timeout_s:
        print(".", end="")
        time.sleep(0.5)
    print()
    if wlan.isconnected():
        print("[WiFi] Conectado! IP:", wlan.ifconfig()[0])
    else:
        print("[WiFi] Falha ao conectar")
    return wlan.isconnected()


def is_online():
    return (not simulated_offline) and wlan.isconnected()


def post_telemetry(payload):
    """Envia uma leitura ao backend. Retorna o JSON de resposta ou None."""
    try:
        url = BACKEND_URL + "/api/telemetry"
        body = json.dumps(payload)
        headers = {"Content-Type": "application/json", "X-Device-Token": DEVICE_TOKEN}
        try:
            resp = urequests.post(url, data=body, headers=headers, timeout=HTTP_TIMEOUT_S)
        except TypeError:  # firmwares antigos sem suporte a timeout
            resp = urequests.post(url, data=body, headers=headers)
        ok = resp.status_code == 200
        data = resp.json() if ok else None
        if not ok:
            print("[HTTP] Erro", resp.status_code, resp.text)
        resp.close()
        return data
    except Exception as e:  # noqa
        print("[HTTP] Falha no envio:", e)
        return None
    finally:
        gc.collect()


def flush_buffer():
    global last_ai
    while offline_buffer and is_online():
        data = post_telemetry(offline_buffer[0])
        if data is None:
            break
        offline_buffer.pop(0)
        last_ai = data
        print("[BUFFER] Leitura sincronizada. Restantes:", len(offline_buffer))


# ================================================================ Feedback
def update_actuators(level):
    global blink_state
    blink_state = not blink_state
    led_green.value(1 if level == NORMAL else 0)
    if level == CRITICO:
        led_red.value(1)
        buzzer.duty(512 if blink_state else 0)
    elif level == ATENCAO:
        led_red.value(1 if blink_state else 0)
        buzzer.duty(0)
    else:
        led_red.value(0)
        buzzer.duty(0)


def update_display(r, level):
    oled.fill(0)
    net = "ON" if is_online() else "OFF"
    oled.text("CardioIA " + net, 0, 0)
    if offline_buffer:
        oled.text("B:{}".format(len(offline_buffer)), 98, 0)
    oled.hline(0, 10, 128, 1)
    oled.text("FC:{} SpO2:{}%".format(r["bpm"], r["spo2"]), 0, 14)
    oled.text("T:{}C PA:{}".format(r["temperature"], r["systolic"]), 0, 25)
    oled.text("Edge: " + level, 0, 37)
    prob = last_ai.get("probabilidade")
    ia = last_ai.get("classificacao_ml") or "--"
    ia = ia.replace("RISCO ", "").replace(" RISCO", "")  # cabe no display
    oled.text("IA: {} {}".format(ia, "{}%".format(round(prob * 100)) if prob is not None else ""), 0, 49)
    oled.show()


# ============================================================ Serial (teste)
def handle_serial():
    global simulated_offline
    while poller.poll(0):
        ch = sys.stdin.read(1)
        if ch == "0":
            simulated_offline = True
            print("\n>>> MODO OFFLINE SIMULADO: leituras serão armazenadas no buffer local")
        elif ch == "1":
            simulated_offline = False
            print("\n>>> RECONECTADO: sincronizando buffer...")
            connect_wifi()


# ==================================================================== Main
def banner():
    print("=" * 52)
    print(" CardioIA - Fase 7 | Edge MicroPython (ESP32)")
    print(" Backend:", BACKEND_URL)
    print(" Comandos: '0' offline | '1' online")
    print("=" * 52)


def main():
    global last_ai
    banner()
    oled.fill(0)
    oled.text("CardioIA", 32, 20)
    oled.text("Iniciando...", 16, 36)
    oled.show()
    connect_wifi()

    last_read = time.ticks_ms() - READ_INTERVAL_MS
    level = NORMAL
    reading = read_sensors()

    while True:
        handle_serial()

        if time.ticks_diff(time.ticks_ms(), last_read) >= READ_INTERVAL_MS:
            last_read = time.ticks_ms()
            reading = read_sensors()
            level, alerts = classify(reading["bpm"], reading["spo2"], reading["temperature"], reading["systolic"])

            payload = dict(reading)
            payload.update({
                "device_id": DEVICE_ID,
                "edge_status": level,
                "edge_alerts": alerts,
                "uptime_s": time.ticks_ms() // 1000,
            })
            print("[EDGE] FC={bpm} SpO2={spo2}% T={temperature}C PA={systolic} -> ".format(**reading)
                  + level + (" " + str(alerts) if alerts else ""))

            if is_online():
                flush_buffer()
                data = post_telemetry(payload)
                if data:
                    last_ai = data
                    print("[IA] Backend:", data.get("nivel"), "| ML:", data.get("classificacao_ml"),
                          "| prob:", data.get("probabilidade"))
                else:
                    offline_buffer.append(payload)
            else:
                if not simulated_offline:
                    connect_wifi(timeout_s=3)
                offline_buffer.append(payload)
                print("[OFFLINE] Leitura armazenada no buffer ({} itens)".format(len(offline_buffer)))

            if len(offline_buffer) > BUFFER_MAX:
                offline_buffer.pop(0)  # descarta a mais antiga

        update_actuators(level)
        update_display(reading, level)
        time.sleep_ms(250)


main()
