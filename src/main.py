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
        sdk.set_led_colors_flush_buffer()

    receiver.register_listener("universe", callback, universe=universe)
    print(f"Created sacn receiver for {name} on universe {universe}, with {len(led_ids)} leds")

def remove_sacn_listener(universe):
    universe = universe
    receiver._callbacks[universe] = ""
    sdk.request_control()
    sdk.release_control()
    
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

def subscribe_device_effect_command_topics(device, base_topic, universe):  #handle device effect command topic; supported are "None", "iCUE", "sACN"
    command_topic = str(str(base_topic) + "/" + str(device) + "/effect/command")
    state_topic = str(str(base_topic) + "/" + str(device) + "/effect/state")
    print(f"subscribed to {command_topic}")
    print(f"puiblishing to {state_topic}")
    client.subscribe(command_topic)
    def callback(client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        if payload == "iCUE":
           universe = conf[device_name.model]
           client.publish(state_topic, payload=payload, qos=0, retain=True)
           remove_sacn_listener(universe)
        if payload == "sACN":
            universe = conf[device_name.model]
            device_test_count = sdk.get_device_count()
            for device_test_index in range(device_test_count):
                device_test_name = sdk.get_device_info(device_test_index)
                if device_test_name.model == device_name.model:
                    device_hi = device_test_index
                    setup_receiver(universe, device_hi)
                    client.publish(state_topic, payload=payload, qos=0, retain=True)
        if payload == "None":
            print("removing")
            client.publish(state_topic, payload=payload, qos=0, retain=True)
            universe = conf[device_name.model]
            remove_sacn_listener(universe)
            client.publish(state_topic, payload=payload, qos=0, retain=True)

            
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
    data['color_mode'] = "true"
    data['supported_color_modes'] = ["rgb"]
    data['effect'] = "true"
    data['effect_list'] = ["None", "sACN", "iCUE"]
    data['device'] = device_data
    payload = json.dumps(data)
    print(f"publishing device info for: {device_name}")
    print(f"at topic: {device_info_topic}")
    client.publish(device_info_topic, payload, qos=0, retain=True)

def setup_use_exclusive_control(base_topic):
    topic = str(str(base_topic) + "iCUE2sACN/iCUE_exclusive_control")
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
    topic = str(str(base_topic) + "/light/iCUE_device_layer")
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



device_data = {}
device_data['name'] = "iCUE2sACN"
device_data['identifiers'] = "iCUE2sACN"
device_data['manufacturer'] = "tenn0"
conf = load_config(DEVICE_PATH)  #load device config
mqtt_conf = load_config(MQTT_PATH) #load mqtt config
mqtt_broker_ip = mqtt_conf['ip']  #setup mqtt
mqtt_broker_port = mqtt_conf['port']
mqtt_user = mqtt_conf['username']
mqtt_pass = mqtt_conf['password']
mqtt_base_topic = mqtt_conf['base_topic']
light_topic = mqtt_base_topic + "/light/iCUE2sACN"
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

setup_use_exclusive_control(light_topic)
setup_layer_priority(light_topic)

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
    device_topic_name_short = device_name.model.replace(" ", "_")
    subscribe_device_command_topics(device_topic_name_short, light_topic)
    subscribe_device_effect_command_topics(device_topic_name_short, light_topic, universe)
    publish_device_info(light_topic, device_name.model, device_topic_name_short)

client.loop_forever()