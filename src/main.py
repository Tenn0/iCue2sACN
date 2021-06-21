from os import times
from cuesdk import CueSdk
import json
import sacn
import time


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


receiver = sacn.sACNreceiver() #sACN receiver  
receiver.start()
sdk = CueSdk() #Corsair iCue SDK
sdk.connect()
sdk.set_layer_priority(128)
with open('config.json') as f:  #Config
      conf = json.load(f)
      print(conf)

device_count = sdk.get_device_count() #setup Corsair devices config
for device_index in range(device_count):
    device_name = sdk.get_device_info(device_index)
    exists = device_name.model in conf
    if exists == False:
        print("Error!!!!!")
    universe = conf[device_name.model] 
    setup_receiver(universe, device_index)

