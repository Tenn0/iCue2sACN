from os import times
from cuesdk import CueSdk
import sacn
import time

def setup_receiver(device_index):
    name = sdk.get_device_info(device_index)
    led_info = sdk.get_led_positions_by_device_index(device_index)
    led_ids = tuple(led_info.keys())
    led_buffer = {led_id: (0, 0, 0) for led_id in led_ids}
    universe = device_index + 1

    def callback(packet):
        data = packet.dmxData

        for x, led_id in enumerate(led_ids):
            led_buffer[led_id] = (data[3*x], data[3*x+1], data[3*x+2])

        sdk.set_led_colors_buffer_by_device_index(device_index, led_buffer)
        sdk.set_led_colors_flush_buffer()

    receiver.register_listener("universe", callback, universe=universe)
    print(f"Created sacn receiver for {name} on universe {universe}, with {len(led_ids)} leds")


receiver = sacn.sACNreceiver()
receiver.start()
sdk = CueSdk()
sdk.connect()
sdk.set_layer_priority(128)

device_count = sdk.get_device_count()

for device_index in range(device_count):
    setup_receiver(device_index)

