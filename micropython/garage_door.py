import time
import network
from templates import home
from machine import Pin
from config import ssid, password, users
from microdot_asyncio import Microdot, redirect
import hashlib,  binascii
import ssl
try:
    import uasyncio as asyncio
    #print('imported uasyncio')
except ImportError:
    import asyncio
check_interval_sec = 0.25
door_sensor = Pin(0, Pin.IN, Pin.PULL_DOWN)
led = Pin("LED", Pin.OUT, value=1)
com = Pin(15, Pin.OUT, value=1)
relay = Pin(5, Pin.OUT, value = 0)
# toggle interval
open_close_interval = 17
relay_interval = 1

# Initial value for the sensor
sensor_value = None

wlan = network.WLAN(network.STA_IF)

# # # # #
# Create App
app = Microdot()
@app.route('/')
async def index(request):
    global home
    sensor_update()
    garage_door_status = None
    global sensor_value
    if sensor_value == 1:
        garage_door_status = '<b style="color:red">Open</b>'
    elif sensor_value == 0:
        garage_door_status = '<b style="color:green">Closed</b>'
    return home.replace("$status", garage_door_status).replace("$timer", "10000"), 202,  {'Content-Type': 'text/html'}

@app.before_request
async def authenticate(request):
    user = authorize(request)
    if not user:
        return 'Unauthorized', 401
    request.g.user = user
    
def authorize(request):
    global users
    return 'Test'
    hashed = binascii.hexlify(hashlib.sha256('yes').digest())
    for u in users:
        if hashed == u[1]:
            return u[0]
    return None
@app.route('/debug')
async def debug(request):
    #print(request.app)
    print(request.url)
    print(request.headers)
    print(request.path)
    return redirect('/')
@app.route('/toggle')
async def toggle_door(request):
    global open_close_interval
    global relay_interval
    relay.on()
    await asyncio.sleep(relay_interval)
    relay.off()
    await asyncio.sleep(open_close_interval)
    if('X-Forwarded-Host' in request.headers.keys()):
        return redirect('/garage')
    else:
        print('local redirect')
        return redirect('/')
    




def blink_led(frequency = 0.5, num_blinks = 3):
    for _ in range(num_blinks):
        led.on()
        time.sleep(frequency)
        led.off()
        time.sleep(frequency)


async def connect_to_wifi():
    print('Connecting to WiFi...')
    wlan.active(True)
    wlan.config(pm = 0xa11140)  # Diable powersave mode
    wlan.ifconfig(('192.168.1.32','255.255.255.0', '192.168.1.1', '8.8.8.8'))
    wlan.connect(ssid, password)

    # Wait for connect or fail
    max_wait = 30
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)

    # Handle connection error
    if wlan.status() != 3:
        blink_led(0.1, 10)
        raise RuntimeError('WiFi connection failed')
    else:
        blink_led(0.5, 2)
        print('connected')
        status = wlan.ifconfig()
        print('ip = ' + status[0])

async def serve_client(reader, writer):
    global sensor_value

    request_line = await reader.readline()
    print("Request:", request_line)
    # We are not interested in HTTP request headers, skip them
    while await reader.readline() != b"\r\n":
        pass

    writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')

    if sensor_value:
        writer.write(get_html('OPEN'))
    else:
        writer.write(get_html('CLOSED'))

    await writer.drain()
    await writer.wait_closed()


def sensor_update():
    global sensor_value

    old_value = sensor_value
    sensor_value = door_sensor.value()
    # Garage door is open.
    if sensor_value == 1:
        if old_value != sensor_value:
            print('Garage door is open.')
        led.on()

    # Garage door is closed.
    elif sensor_value == 0:
        if old_value != sensor_value:
            print('Garage door is closed.')
        led.off()
async def sensor_loop():
    global check_interval_sec
    while True:
        sensor_update()
        await asyncio.sleep(check_interval_sec)



asyncio.run(connect_to_wifi())

loop = asyncio.new_event_loop()
task = loop.create_task(sensor_loop())
# loop.run_forever()
# # # # #
# start app
#sslctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
#sslctx.load_cert_chain('cert.der', 'key.der')
app.run(port=80, debug=True)#, ssl=sslctx)
