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
import framebuf
import network
import urequests
from machine import ADC, I2C, PWM, Pin
from micropython import const

try:
    from ssd1306 import SSD1306_I2C
except ImportError:
    # Fallback embutido caso a aba ssd1306.py não tenha sido criada no Wokwi
    class SSD1306_I2C(framebuf.FrameBuffer):
        def __init__(self, width, height, i2c, addr=0x3C, external_vcc=False):
            self.width = width
            self.height = height
            self.i2c = i2c
            self.addr = addr
            self.external_vcc = external_vcc
            self.pages = self.height // 8
            self.buffer = bytearray(self.pages * self.width)
            self.temp = bytearray(2)
            self.write_list = [b"\x40", None]
            super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
            for cmd in (
                const(0xAE), const(0x20), 0x00, const(0x40), const(0xA1),
                const(0xA8), self.height - 1, const(0xC8), const(0xD3), 0x00,
                const(0xDA), 0x02 if self.width > 2 * self.height else 0x12,
                const(0xD5), 0x80, const(0xD9), 0x22 if self.external_vcc else 0xF1,
                const(0xDB), 0x30, const(0x81), 0xFF, const(0xA4), const(0xA6),
                const(0xAD), 0x30, const(0x8D), 0x10 if self.external_vcc else 0x14,
                const(0xAF),
            ):
                self.write_cmd(cmd)
            self.fill(0)
            self.show()

        def write_cmd(self, cmd):
            self.temp[0] = 0x80
            self.temp[1] = cmd
            self.i2c.writeto(self.addr, self.temp)

        def show(self):
            for cmd in (const(0x21), 0, self.width - 1, const(0x22), 0, self.pages - 1):
                self.write_cmd(cmd)
            self.write_list[1] = self.buffer
            self.i2c.writevto(self.addr, self.write_list)


# ------------------------------------------------------------- Configuração
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASSWORD = ""
BACKEND_URL = "https://cardioia-backend-ewbv.onrender.com"  # <- URL pública do Render
DEVICE_TOKEN = "cardioia-device-demo-token"            # <- mesmo valor de DEVICE_TOKEN no backend
DEVICE_ID = "cardioia-esp32-01"

READ_INTERVAL_MS = 5000      # período de leitura/envio
HTTP_TIMEOUT_S = 15          # Render free pode "acordar" lentamente
BUFFER_MAX = 20              # leituras guardadas quando offline

# ------------------------------------------------------------------- Estado
# Inicia o rádio Wi-Fi antes de configurar ADC/PWM/I2C para acelerar o handshake no Wokwi
wlan = network.WLAN(network.STA_IF)
try:
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
except OSError:
    pass

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
buzzer_pin = Pin(25, Pin.OUT, value=0)
buzzer_pwm = None

i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)

simulated_offline = False
offline_buffer = []
last_ai = {"classificacao_ml": "--", "probabilidade": None, "nivel": "--"}
blink_state = False
wifi_logged = False

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
def estimate_ai_edge(r, level):
    """Fallback local de risco caso o gateway Wi-Fi do Wokwi esteja indisponível."""
    score = 0.12
    if r["systolic"] >= 180 or r["systolic"] < 90:
        score += 0.42
    elif r["systolic"] >= 140:
        score += 0.25
    if r["bpm"] > 120 or r["bpm"] < 50:
        score += 0.25
    elif r["bpm"] > 100 or r["bpm"] < 60:
        score += 0.12
    if r["spo2"] < 90:
        score += 0.22
    elif r["spo2"] < 95:
        score += 0.10
    if r["temperature"] >= 39.0 or r["temperature"] < 35.0:
        score += 0.15
    elif r["temperature"] >= 37.6:
        score += 0.08
    prob = min(0.98, round(score, 2))
    if prob >= 0.65 or level == CRITICO:
        ml_cls = "ALTO RISCO"
    elif prob >= 0.35 or level == ATENCAO:
        ml_cls = "RISCO MODERADO"
    else:
        ml_cls = "BAIXO RISCO"
    return {"classificacao_ml": ml_cls, "probabilidade": prob, "nivel": level}


def connect_wifi(timeout_s=8):
    global wifi_logged
    if wlan.isconnected():
        if not wifi_logged:
            print("[WiFi] Conectado! IP:", wlan.ifconfig()[0])
            wifi_logged = True
        return True
    try:
        wlan.active(True)
        if wlan.status() != getattr(network, "STAT_CONNECTING", 1001):
            wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        print("[WiFi] Conectando a", WIFI_SSID, end="")
    except OSError as e:
        print("\n[WiFi] Aviso ao iniciar conexao:", e)

    start = time.ticks_ms()
    while not wlan.isconnected() and time.ticks_diff(time.ticks_ms(), start) < timeout_s * 1000:
        print(".", end="")
        time.sleep_ms(100)
    print()
    if wlan.isconnected():
        print("[WiFi] Conectado! IP:", wlan.ifconfig()[0])
        wifi_logged = True
    else:
        print("[WiFi] Aguardando gateway Wokwi (status={}) - operando com resiliencia Edge".format(wlan.status()))
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
def set_buzzer(active):
    global buzzer_pwm
    if active:
        if buzzer_pwm is None:
            buzzer_pwm = PWM(Pin(25), freq=2000, duty=512)
        else:
            buzzer_pwm.duty(512)
    else:
        if buzzer_pwm is not None:
            buzzer_pwm.deinit()
            buzzer_pwm = None
            Pin(25, Pin.OUT, value=0)


def update_actuators(level):
    global blink_state
    blink_state = not blink_state
    led_green.value(1 if level == NORMAL else 0)
    if level == CRITICO:
        led_red.value(1)
        set_buzzer(blink_state)
    elif level == ATENCAO:
        led_red.value(1 if blink_state else 0)
        set_buzzer(False)
    else:
        led_red.value(0)
        set_buzzer(False)


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
    global last_ai, wifi_logged
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
                if not wifi_logged:
                    print("[WiFi] Conectado em segundo plano! IP:", wlan.ifconfig()[0])
                    wifi_logged = True
                flush_buffer()
                data = post_telemetry(payload)
                if data:
                    last_ai = data
                    print("[IA] Backend:", data.get("nivel"), "| ML:", data.get("classificacao_ml"),
                          "| prob:", data.get("probabilidade"))
                else:
                    last_ai = estimate_ai_edge(reading, level)
                    offline_buffer.append(payload)
            else:
                last_ai = estimate_ai_edge(reading, level)
                offline_buffer.append(payload)
                print("[OFFLINE] Buffer={} | IA Edge={} (prob={})".format(
                    len(offline_buffer), last_ai["classificacao_ml"], last_ai["probabilidade"]))

            if len(offline_buffer) > BUFFER_MAX:
                offline_buffer.pop(0)  # descarta a mais antiga

        update_actuators(level)
        update_display(reading, level)
        time.sleep_ms(250)


main()
