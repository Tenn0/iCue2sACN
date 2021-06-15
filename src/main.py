from os import times
from cuesdk import CueSdk
from pathlib import Path
import paho.mqtt.client as mqtt
import json
import sacn
import time

def on_connect(client, userdata, flags, rc):
      print("Connected with result code "+str(rc))
      client.subscribe("hi/#")

def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    print(msg.payload)
    print(payload)
    if str(payload) == "lol":
        print("this works bruh!")
        client.publish("hi/ho", payload="hello there!", qos=0, retain=False)

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



with open('config.json') as f:
      d = json.load(f)
      print(d)
mqtt_broker_ip = d['ip']
mqtt_broker_port = d['port']
mqtt_user = d['username']
mqtt_pass = d['password']

receiver = sacn.sACNreceiver()
receiver.start()
sdk = CueSdk()
sdk.connect()
sdk.set_layer_priority(128)
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(mqtt_user, password=mqtt_pass)
client.connect(mqtt_broker_ip, mqtt_broker_port, keepalive = 60, bind_address="" )

device_count = sdk.get_device_count()

for device_index in range(device_count):
    setup_receiver(device_index)

client.loop_forever()