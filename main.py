import network
import socket
import time
from machine import Pin, PWM

# Configurare Servomotor 
servo = PWM(Pin(15))
servo.freq(50)

# Calibrare 
def set_angle(angle):
    if angle < 0: 
        angle = 0
    if angle > 90: 
        angle = 90
    
    min_duty = 1638  
    max_duty = 4915  
    
    duty = int(min_duty + (angle / 90) * (max_duty - min_duty))
    servo.duty_u16(duty)

# Initializare
running = False
angle = 0
direction = 1

led = Pin("LED", Pin.OUT)

# Configurare AP
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="PICO-SERVO", password="12345678")

print("WiFi Access Point activ: PICO-SERVO")
print("Adresa IP: 192.168.4.1")

# Pagina Web HTML
html = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Pico Servo 90</title>
    <style>
        body { font-family: sans-serif; text-align:center; background:#f0f0f0; padding-top:50px; }
        .box { background: white; display: inline-block; padding: 20px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
        button { width:180px; height:70px; font-size:22px; margin:15px; border:none; border-radius:12px; cursor:pointer; color:white; font-weight:bold; }
        .start { background:#2ecc71; }
        .stop { background:#e74c3c; }
        .status { color: #666; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="box">
        <h1>Control Servo 90&deg;</h1>
        <button class="start" onclick="fetch('/on')">START</button>
        <button class="stop" onclick="fetch('/off')">STOP</button>
        <div class="status">Pico W este gata de comenzi</div>
    </div>
</body>
</html>
"""

# Pornire Web Server
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)
s.settimeout(0.02) 

print("Server pornit pe portul 80...")

# Bucla principala
while True:
    if running:
        set_angle(angle)
        angle += direction * 2
        if angle >= 90 or angle <= 0:
            direction *= -1
        time.sleep(0.02)
    try:
        cl, addr = s.accept()
        request = cl.recv(1024)
        request = str(request)

        if '/on' in request:
            running = True
            led.on()
            print("Comandă primită: START")
        elif '/off' in request:
            running = False
            led.off()
            print("Comandă primită: STOP")
        cl.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n')
        cl.sendall(html)
        cl.close()
        
    except OSError:
        pass
