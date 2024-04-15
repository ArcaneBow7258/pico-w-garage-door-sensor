# Raspberry Pi Pico W Garage Door Sensor
Orignal Link:
[![Lint](https://github.com/geerlingguy/pico-w-garage-door-sensor/actions/workflows/lint.yml/badge.svg?branch=master)](https://github.com/geerlingguy/pico-w-garage-door-sensor/actions/workflows/lint.yml)

Mostly the same but wanted to add integration of technologies/codebases I was more familiar in (specifically microdot)
[Microdot](https://microdot.readthedocs.io/en/latest/) is a micropython library that acts very similar to the format of Flask for regular Python.

## Supplies
- [5V relay](https://www.amazon.com/dp/B00LW15A4W) (1 Channel per Garage door you're interested in)
- [Magnetic Swithes](https://www.amazon.com/dp/B086GYJLM)
  - You could use limit/physical switchese I'd imagine you just need some circuit to be compeleted when closed.
- Pico W (obviously)
- Bread Board
- Wires (long enough)
- Power supply

## Wiring 
1. Relay
  - DC+ -> V_out or 3.3V (really always-on voltage)
    - So technically the relay is 5V which might might be an issue with Pico W being a 3.3V device... so external power is preferable
  - DC- -> Ground
  - IN -> Relay Pin in your code (the toggler)
  - COM -> 5v of Garage
  - NO (normally open) -> Input of garage
    - You might need to do research of what your garage wiring interface looks like 
2. Magnetic Switches
  - COM -> V_out or 3.3V
  - NO -> Input pin for Garage Door
## Preparing to flash the Pico W

Create a config.py file with variables of `ssid, password` and optionally a `users` list of tuples.
- Optional to use a `@app.before_request` to authetnicate the user using SHA256
- So your list should be [(User1, SHA256 hash in byte data type), (User2....)]
- Just a really simple 'password check' if you need an extra layer
  - Note, technically anyone plugged into your PicoW can read that config file so if any risk of that think about it a little. 

## External Connection
So theres multiple ways of going by this:
1. Port-forwarding your Pico W to the open internet (easy but bad if someone cares)
2. Reverse Proxy it? (Ngninx?)
  - NGINX also allows for [authentication](https://docs.nginx.com/nginx/admin-guide/security-controls/configuring-http-basic-authentication/) per page which is nice 
3. VPN and access through that (current config).
   - I set up Wireguard on an internal device which is port-forwarded to open internet
   - Exchange Public Keys between internal server and client you'd like be able to use the Pico W
   - Set up NGINX to redirect ports on internal server to Pico W's internal IP (i.e., redirect '/' to '192.168.2.10' which is Pico's Address locally

