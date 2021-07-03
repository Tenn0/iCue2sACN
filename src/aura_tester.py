import json
from typing import Sequence
import win32com.client
import time
import sacn
import webcolors
import json
import sys
import os

DEVICE_PATH = 'config2.json'
MQTT_PATH = 'mqtt.json'



def get_free_universe():
    return next(
        i
        for i in range(1, 128)
        if i not in conf.values()
    )

def load_config(config_path):
    if not os.path.isfile(config_path):  #Create the file if not present
        open(config_path, "w+")
    if config_path == MQTT_PATH:
         with open(config_path) as f:  #load the config file
            try:
                return json.load(f)
            except json.JSONDecodeError:
                data = {}
                data['enable_MQTT'] = True
                data['ip'] =""
                data['port']= 1883
                data['username'] =""
                data['password'] =""
                data['base_topic'] =""
                with open(config_path, "w", encoding="utf-8") as f:  # Save config
                    json.dump(
                        data,
                        f, 
                        ensure_ascii=False,
                        sort_keys=False,
                        indent=4
                        )
                print(f"MQTT Config Created, please edit {MQTT_PATH} and restart this program!")
                print("For Home Assistant Auto Discovery, set base_topic to homeassistant!")
                sys.exit()
                
    with open(config_path) as f:  #load the config file
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}   

def save_config(config_path):
    with open(config_path, "w", encoding="utf-8") as f:  # Save config
        json.dump(
            conf,
            f, 
            ensure_ascii=False,
            sort_keys=True,
            indent=4
        )

def setup_receiver(universe, device_index):
    print(f"setting up device {device_index}")
    led_ids = dev.Lights.count
    led_buffer = {x: (0, 0, 0) for x in range(led_ids)}
    universe = universe

    def callback(packet):
        data = packet.dmxData
        for i in range(led_ids):
            led_buffer[i] = (data[3*i], data[3*i+1], data[3*i+2])
            dev.Lights(i).Red = data[3*1]
            dev.Lights(i).Green = data[3*i+1]
            dev.Lights(i).Blue = data[3*i+2] 
        dev.Apply()

    receiver.register_listener("universe", callback, universe=universe)
    print(f"Created sacn receiver for {device_index} on universe {universe}, with {led_ids} leds")
print("started")
auraSdk = win32com.client.Dispatch("aura.sdk.1")
print("aurasdk intiallized")
auraSdk.SwitchMode()
print("aura mode switched")
start = time.process_time_ns()
print(start)
devices = auraSdk.Enumerate(0)
print(time.process_time_ns())
print(time.process_time_ns() - start)
print(devices)

receiver = sacn.sACNreceiver() #sACN receiver  
receiver.start()
print("sACN receiver started")
print(f"setting up devices: {devices}")
#print(type(devices))
conf = load_config(DEVICE_PATH)  #load device config
i = 0
for dev in devices:
    print("hi")
    print(i)
    device_name = str(dev)+" aura"
    print(device_name)
    led_ids = dev.Lights.count
    print(led_ids)
    led_buffer = {x: (0, 0, 0) for x in range(led_ids)}
    universe = get_free_universe() + i

    print(type(led_buffer))
    setup_receiver(universe, dev)
    print(universe)
    print("Hello There!")
    i = i +1
    