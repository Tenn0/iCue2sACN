from os import times
from cuesdk import CueSdk
import json
import sacn
import time
import paho.mqtt.client as mqtt


DEVICE_PATH = 'config.json'
MQTT_PATH = 'mqtt.json'

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
        for i in range(1, 128)
        if i not in conf.values()
    )

def load_config(config_path):
    with open(config_path) as f:  #Config
        try:
            return json.load(f)
        except OSError:
            print("file not there, creating it")
            open(config_path, "x")
        except json.JSONDecodeError:
            return {}
            

def save_config(config_path):
    with open(config_path, "w", encoding="utf-8") as f:  # Save config
        json.dump(
            conf,2
            f, 
            ensure_ascii=False,
            sort_keys=True,
            indent=4
        )

conf = load_config(DEVICE_PATH)  #load device confiug
mqtt_conf = load_config(MQTT_PATH) #load mqtt config
mqtt_broker_ip = mqtt_conf['ip']  #setup mqtt
mqtt_broker_port = mqtt_conf['port']
mqtt_user = mqtt_conf['username']
mqtt_pass = mqtt_conf['password']
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(mqtt_user, password=mqtt_pass)
client.connect(mqtt_broker_ip, mqtt_broker_port, keepalive = 60, bind_address="" )


receiver = sacn.sACNreceiver() #sACN receiver  
receiver.start()
sdk = CueSdk() #Corsair iCue SDK
sdk.connect()
sdk.set_layer_priority(128)



device_count = sdk.get_device_count() #setup Corsair devices config
for device_index in range(device_count):
    device_name = sdk.get_device_info(device_index)
    if device_name.model not in conf:
        universe = get_free_universe()
        conf.update({device_name.model: universe}) 
        print(f"conf= {conf}")
    else:
        universe = conf[device_name.model] 
    save_config(DEVICE_PATH)
    setup_receiver(universe, device_index)

