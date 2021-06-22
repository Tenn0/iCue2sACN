from os import times
from cuesdk import CueSdk
import json
import sacn
import time

JSON_PATH = 'config.json'

def setup_receiver(universe, device_index):
    name = sdk.get_device_info(device_index)
    led_info = sdk.get_led_positions_by_device_index(device_index)
    led_ids = tuple(led_info.keys())
    led_buffer = {led_id: (0, 0, 0) for led_id in led_ids}
    universe = universe

    def callback(packet):
        data = packet.dmxData

        for x, led_id in enumerate(led_ids):
            led_buffer[led_id] = (data[3*x], data[3*x+1], data[3*x+2])

        sdk.set_led_colors_buffer_by_device_index(device_index, led_buffer)
        sdk.set_led_colors_flush_buffer()

    receiver.register_listener("universe", callback, universe=universe)
    print(f"Created sacn receiver for {name} on universe {universe}, with {len(led_ids)} leds")

def get_free_universe():
    return next(
        i
        for i in range(128)
        if i not in conf.values()
    )

def load_config(config_path):
    with open(config_path) as f:  #Config
        return json.load(f)

def save_config(config_path):
    with open(config_path) as f:  #Config
        json.dump(f)

receiver = sacn.sACNreceiver() #sACN receiver  
receiver.start()
sdk = CueSdk() #Corsair iCue SDK
sdk.connect()
sdk.set_layer_priority(128)

conf = load_config(JSON_PATH)

device_count = sdk.get_device_count() #setup Corsair devices config
for device_index in range(device_count):
    device_name = sdk.get_device_info(device_index)
    if device_name.model not in conf:
        universe = get_free_universe()
        conf.update({device_name.model: universe}) 
        print(f"conf= {conf}")
    else:
        universe = conf[device_name.model] 
    save_config(JSON_PATH)
    setup_receiver(universe, device_index)

