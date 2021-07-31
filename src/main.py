from cuesdk import CueSdk
import json
from cuesdk.enums import CorsairLedId
import sacn
import time
import paho.mqtt.client as mqtt
import os
import sys
import math

DEVICE_PATH = 'config.json'
MQTT_PATH = 'mqtt.json'
COLOR_PATH = 'colors.json'

def map(x, in_min, in_max, out_min, out_max):
    return (x-in_min) * (out_max-out_min) / (in_max - in_min) + out_max

def map_brightness_to_percentage(val):
    x = map(val, 0,255,0,100)
    return x

def save_device_colors(device_name, color):
    conf = (str(device_name) + str(color)) 
    with open(COLOR_PATH, "a", encoding="utf-8") as f:  # Save config
        json.dump(
            conf,
            f, 
            ensure_ascii=False,
            sort_keys=True,
            indent=4
        )
    print("saved colors")
    return 1

def load_device_colors(device_name):
    if not os.path.isfile(COLOR_PATH):  #Create the file if not present
        open(COLOR_PATH, "w+")
    with open(COLOR_PATH) as f:  #load the config file
        try:
            color = json.load(f)
            print(type(color))
            color = color.removesuffix(device_name)
            print(f"current color for {device_name} is {color}")
            return color
        except json.JSONDecodeError:
            print("JSON ERROR opening colors file")

def get_device_index_by_name(device_name):
    device_count = sdk.get_device_count()
    for device_index in range(device_count):
        device_test_name = sdk.get_device_info(device_index)
        if device_test_name.model == device_name:
            return device_index

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

def set_all_device_leds(device_index, color):
    led_info = sdk.get_led_positions_by_device_index(device_index)
    led_ids = tuple(led_info.keys())
    led_buffer = {led_id: (0, 0, 0) for led_id in led_ids}
    for x, led_id in enumerate(led_ids):
        led_buffer[led_id] = (color['r'], color ['g'], color['b'])
        sdk.set_led_colors_buffer_by_device_index(device_index, led_buffer)
        sdk.set_led_colors_flush_buffer()

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

def setup_device_command_topics(device_short, device, base_topic):  #subscribe to device state topic and publish on message dynically
    command_topic = str(str(base_topic) + "/" + str(device_short) + "/command")
    state_topic = str(str(base_topic) + "/" + str(device_short) + "/state")
    print(f"subscribed to {command_topic}")
    print(f"publishing to {state_topic}")
    client.subscribe(command_topic)
    def callback(client, userdata, msg):
        device_index = get_device_index_by_name(device)
        universe = conf[device]
        payload = msg.payload.decode("utf-8")
        payload = json.loads(payload)
        state_payload = {}
        if payload["state"] == "ON" and "effect" in payload:    #effect changed
            print("effect changed")
            if payload['effect'] == "sACN":
                device_index = get_device_index_by_name(device)
                setup_receiver(universe, int(device_index))
                state_payload['effect'] = "sACN"
            if payload['effect'] == "iCUE":
                receiver.remove_listener_from_universe(universe)
                state_payload['effect'] = "iCUE"
        elif  not "effect" and "color" in payload: #effect == none, color
            print("color changed, no effect")
            universe = conf[device]
            receiver.remove_listener_from_universe(universe)
            set_all_device_leds(device_index, payload['color'])
            print(f"setting colors to {payload['color']}")
            state_payload['color'] = payload['color']
        elif payload['state'] == "ON" and not "effect" in payload and "color" in payload: # color changed
            print(f"color changed on {device}")
            save_device_colors(device, payload["color"])
            receiver.remove_listener_from_universe(universe)
            set_all_device_leds(device_index, payload['color'])
            state_payload['color'] = payload['color']
            state_payload['brightness'] = "255" 
            state_payload["state"] = "ON"
        elif payload['state'] == "OFF": #state off
            print("state off")
            receiver.remove_listener_from_universe(universe) 
            color = {}
            color['r'] = 0
            color['g'] = 0
            color['b'] = 0
            set_all_device_leds(device_index, color)
            state_payload = payload
            state_payload['brightness'] = "0"
        elif payload['state'] == "ON" and not "brightness" in payload: #state on
            print("state on")
            receiver.remove_listener_from_universe(universe)
            color = {}
            color['r'] = 255
            color['g'] = 255
            color['b'] = 255
            set_all_device_leds(device_index, color)
            print(f"setting colors to {color}")
            state_payload['state'] = "ON"
            state_payload['color'] = color
            state_payload['brightness'] = "255"
        elif 'brightness' in payload and payload["state"] == "ON": #brightness changed
            print(f"brightness changed: {payload['brightness']}")
            current_color = load_device_colors(device)
            print(f"current color is {current_color}")
            fac = payload['brightness']
            print(fac)
            color = {}
            color['r'] = math.floor(current_color[0] / fac)
            color['g'] = math.floor(current_color[1] / fac)   
            color['b'] = math.floor(current_color[2] / fac)
            set_all_device_leds(device_index, color)
            state_payload["state"] = "ON"
            state_payload["brightness"] = payload["brightness"]
            state_payload["color"] = color
            print(state_payload["color"])


            
        state_payload = json.dumps(state_payload)
        client.publish(state_topic, state_payload, qos=0, retain=True)
    
    client.message_callback_add(command_topic, callback)




def publish_device_info(mqtt_base_topic, device_name, topic_name):
    device_info_topic = str(str(mqtt_base_topic)+"/"+str(topic_name)+"/config")
    data = {}
    data['name'] = str(device_name)
    data['unique_id'] = str(device_name + "_iCUE2sACN")
    data['state_topic'] = str(str(mqtt_base_topic) + "/" + str(topic_name)+ "/state")
    data['command_topic'] = str(str(mqtt_base_topic) + "/" +str(topic_name)+ "/command")
    data['schema'] = "json"
    data['brightness'] = "true"
    data['rgb'] = "true"
    data['effect'] = "true"
    data['effect_list'] = ["None", "sACN", "iCUE"]
    data['device'] = device_data
    payload = json.dumps(data)
    print(f"publishing device info for: {device_name}")
    print(f"at topic: {device_info_topic}")
    client.publish(device_info_topic, payload, qos=0, retain=True)

def setup_use_exclusive_control(base_topic):
    topic = str(str(base_topic) + "/iCUE_exclusive_control")
    command_topic = str(str(topic) + str("/command"))
    state_topic = str(topic + "/state") 
    config_topic = topic + "/config"
    data = {}
    data['name'] = "iCUE Exclusive Control"
    data['unique_id'] = str(data['name'] + "_iCUE2sACN")
    data['state_topic'] = state_topic
    data['command_topic'] = command_topic
    data['device'] = device_data
    config_payload = json.dumps(data)
    client.publish(config_topic, config_payload, qos=0, retain=True)
    client.subscribe(command_topic)
    def callback(client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        if payload == "ON":
            sdk.request_control()
        if payload =="OFF":
            sdk.release_control()
        client.publish(state_topic, payload, qos=0, retain=True)
        
    client.message_callback_add(command_topic, callback)

def setup_layer_priority(base_topic):
    topic = str(str(base_topic) + "/iCUE_device_layer")
    command_topic = str(str(topic) + str("/command"))
    config_topic = topic + "/config"
    state_topic = str(topic + "/state") 
    client.subscribe(command_topic)
    data = {}
    data['name'] = "iCUE Layer Priority"
    data['unique_id'] = str(data['name'] + "_iCUE2sACN")
    data['state_topic'] = state_topic
    data['command_topic'] = command_topic
    data['brightness'] = "true"
    data['schema'] = "json"
    data['device'] = device_data
    config_payload = json.dumps(data)
    client.publish(config_topic, config_payload, qos=0, retain=True )
    def callback(client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        payload2 = json.loads(payload)
        print(str(payload2))
        state_payload = {}
        state_payload['state'] = payload2['state']
        if "brightness" in payload2 :
            state_payload['brightness'] = payload2['brightness']
        #   last_layer_priority = state_payload["brightness"]
            sdk.set_layer_priority(payload2['brightness'])
        #else: 
        #   last_layer_priority = 0
        if payload2['state'] == "OFF":
            sdk.set_layer_priority(0)
        if payload2['state'] == "ON":
        #  state_payload['brightness'] = last_layer_priority
        # sdk.set_layer_priority(last_layer_priority)
            state_payload["brightness"] = "128"
            sdk.set_layer_priority(128)
        state_payload = json.dumps(state_payload)
        client.publish(state_topic, state_payload, qos=0, retain=True)
        
    
    client.message_callback_add(command_topic, callback)



conf = load_config(DEVICE_PATH)  #load device config
mqtt_conf = load_config(MQTT_PATH) #load mqtt config
enable_mqtt = mqtt_conf['enable_MQTT']
if enable_mqtt == True:
    mqtt_broker_ip = mqtt_conf['ip']  #setup mqtt
    mqtt_broker_port = mqtt_conf['port']
    mqtt_user = mqtt_conf['username']
    mqtt_pass = mqtt_conf['password']
    mqtt_base_topic = mqtt_conf['base_topic']
    light_topic = mqtt_base_topic + "/light/iCUE2sACN"
    device_data = {}
    device_data['name'] = "iCUE2sACN"
    device_data['identifiers'] = "iCUE2sACN"
    device_data['manufacturer'] = str(mqtt_user)
    client = mqtt.Client()
print(f"enable mqtt: {enable_mqtt}")
print(type(enable_mqtt))
if enable_mqtt == True:
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(mqtt_user, password=mqtt_pass)
    client.connect(mqtt_broker_ip, mqtt_broker_port, keepalive = 60, bind_address="" )
    setup_use_exclusive_control(light_topic)
    setup_layer_priority(light_topic)


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
    device_topic_name_short = device_name.model.replace(" ", "_")
    setup_receiver(universe, device_index)
    if enable_mqtt == True:
        setup_device_command_topics(device_topic_name_short, device_name.model,  light_topic)
        publish_device_info(light_topic, device_name.model, device_topic_name_short)
if enable_mqtt == True:
    client.loop_forever()





  
