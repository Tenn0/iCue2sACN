from cuesdk import CueSdk
import json
import sacn
import time
import paho.mqtt.client as mqtt
import os

DEVICE_PATH = 'config.json'
MQTT_PATH = 'mqtt.json'

def on_connect(client, userdata, flags, rc):
      print("Connected with result code "+str(rc))
      client.subscribe(mqtt_base_topic) #subscribe to base topic
      client.publish(mqtt_base_topic, str(load_config(DEVICE_PATH))) #dump device_config into base topic


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
        sdk.set_led_colors_flush_buffer_async()

    receiver.register_listener("universe", callback, universe=universe)
    print(f"Created sacn receiver for {name} on universe {universe}, with {len(led_ids)} leds")

def get_free_universe():
    return next(
        i
        for i in range(1, 128)
        if i not in conf.values()
    )

def load_config(config_path):
    if not os.path.isfile(config_path):  #Create the file if not present
        open(config_path, "w+")
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

def subscribe_device_command_topics(device, base_topic):  #subscribe to device state topic and publish on message dynically
    command_topic = str(str(base_topic) + "/" + str(device) + "/command")
    state_topic = str(str(base_topic) + "/" + str(device) + "/state")
    print(f"subscribed to {command_topic}")
    print(f"puiblishing to {state_topic}")
    client.subscribe(command_topic)
    def callback(client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        if payload == "on":
           print("on")
           client.publish(state_topic, payload=payload, qos=0, retain=True) 
        else:
            print("off")
            client.publish(state_topic, payload=payload, qos=0, retain=True)
    
    client.message_callback_add(command_topic, callback)

def subscribe_device_effect_command_topics(device, base_topic):  #subscribe to device state topic and publish on message dynically
    command_topic = str(str(base_topic) + "/" + str(device) + "/effect/command")
    state_topic = str(str(base_topic) + "/" + str(device) + "//effect/state")
    print(f"subscribed to {command_topic}")
    print(f"puiblishing to {state_topic}")
    client.subscribe(command_topic)
    def callback(client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        if payload == "on":
           print("on")
           client.publish(state_topic, payload=payload, qos=0, retain=True) 
        else:
            print("off")
            client.publish(state_topic, payload=payload, qos=0, retain=True)
    
    client.message_callback_add(command_topic, callback)

def subscribe_device_color_command_topics(device, base_topic):  #subscribe to device state topic and publish on message dynically
    command_topic = str(str(base_topic) + "/" + str(device) + "/color/command")
    state_topic = str(str(base_topic) + "/" + str(device) + "/color/state")
    print(f"subscribed to {command_topic}")
    print(f"puiblishing to {state_topic}")
    client.subscribe(command_topic)
    def callback(client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        if payload == "on":
           print("on")
           client.publish(state_topic, payload=payload, qos=0, retain=True) 
        else:
            print("off")
            client.publish(state_topic, payload=payload, qos=0, retain=True)
    
    client.message_callback_add(command_topic, callback)

def subscribe_device_brightness_command_topics(device, base_topic):  #subscribe to device state topic and publish on message dynically
    command_topic = str(str(base_topic) + "/" + str(device) + "/brightness/command")
    state_topic = str(str(base_topic) + "/" + str(device) + "/brightness/state")
    print(f"subscribed to {command_topic}")
    print(f"puiblishing to {state_topic}")
    client.subscribe(command_topic)
    def callback(client, userdata, msg):  #handle msg
        payload = msg.payload.decode("utf-8")
        if payload == "on":
           print("on")
           client.publish(state_topic, payload=payload, qos=0, retain=True) 
        else:
            print("off")
            client.publish(state_topic, payload=payload, qos=0, retain=True)
    
    client.message_callback_add(command_topic, callback)

def publish_device_info(mqtt_base_topic, device_name, device_type, led_count, universe):
    data = {}
    data['name'] = str(device_name)
    data['type'] = str(device_type)
    data['led_count'] = str(led_count)
    data['universe'] = str(universe)
    payload = json.dumps(data)
    device_info_topic = str(str(mqtt_base_topic)+"/"+str(device_name)+"/config")
    print(f"publishing device info for: {device_name}")
    print(f"at topic: {device_info_topic}")
    client.publish(device_info_topic, payload, qos=0, retain=True)




conf = load_config(DEVICE_PATH)  #load device config
mqtt_conf = load_config(MQTT_PATH) #load mqtt config
mqtt_broker_ip = mqtt_conf['ip']  #setup mqtt
mqtt_broker_port = mqtt_conf['port']
mqtt_user = mqtt_conf['username']
mqtt_pass = mqtt_conf['password']
mqtt_base_topic = mqtt_conf['base_topic']
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
    device_type = device_name.type
    if device_name.model not in conf:
        universe = get_free_universe()
        conf.update({device_name.model: universe}) 
        print(f"conf= {conf}")
    else:
        universe = conf[device_name.model] 
    save_config(DEVICE_PATH)
    setup_receiver(universe, device_index)

    subscribe_device_command_topics(device_name.model, mqtt_base_topic)
    subscribe_device_brightness_command_topics(device_name.model, mqtt_base_topic)
    subscribe_device_color_command_topics(device_name.model, mqtt_base_topic)
    subscribe_device_effect_command_topics(device_name.model, mqtt_base_topic)
    publish_device_info(mqtt_base_topic, device_name.model, device_name.type, device_name.led_count, universe )

client.loop_forever()