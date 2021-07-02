import win32com.client
import time
import sacn
import webcolors

print("started")
auraSdk = win32com.client.Dispatch("aura.sdk.1")
print("aurasdk intiallized")
auraSdk.SwitchMode()
print("aura mode switched")
start = time.process_time_ns()
devices = auraSdk.Enumerate(7)
print(time.process_time_ns() - start)
print(devices)

receiver = sacn.sACNreceiver() #sACN receiver  
receiver.start()
print("sACN receiver started")

def setup_receiver(universe, device_index):
    print(f"setting up device {device_index}")
    led_ids = dev.Lights.count
    led_buffer = {x: (0, 0, 0) for x in led_ids}
    universe = universe

    def callback(packet):
        data = packet.dmxData

        for x in range(dev.Lights.count):
            led_buffer[x] = (data[3*x], data[3*x+1], data[3*x+2])
            converted_led_buffer = str("0x00" + webcolors.rgb_to_hex(led_buffer))
            dev.Lights(x).color = converted_led_buffer
            dev.Apply()

    receiver.register_listener("universe", callback, universe=universe)
    print(f"Created sacn receiver for {device_index} on universe {universe}, with {len(led_ids)} leds")

print("setting up devices")
for dev in devices:
    print("hi")
    print(dev)
    setup_receiver(5, dev)
    