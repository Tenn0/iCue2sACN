from os import times
from cuesdk import CueSdk
import sacn
import time


receiver = sacn.sACNreceiver()
receiver.start()
sdk = CueSdk()
sdk.connect()
sdk.set_layer_priority(128)

##vars:
##devices: index, numLeds
device1 = (1, 3)  ##keyboard
device2 = 0  ##mouse
device3 = 2  ##fans
device4 = 3  ##pump

@receiver.listen_on('universe', universe=1)  # listens on universe 1
def callback(packet):  # packet type: sacn.DataPacket
    data = packet.dmxData
    led1 = (data[0], data[1], data[2])
    led2 = (data[3], data[4], data[5])
    led3 = (data[6], data[7], data[8])
    #print(led1)        
    sdk.set_led_colors_buffer_by_device_index(device1[0], {500: led1, 501: led2, 502: led3 })
    sdk.set_led_colors_flush_buffer()
    
    #print(packet.dmxData)  # print the received DMX data
    #pixel1 = (r, g, b)
    #pixel1.r = packet.dmxData[0]
    #print(pixel1.r)
@receiver.listen_on('universe', universe=2)  # listens on universe 1
def callback(packet):  # packet type: sacn.DataPacket
    data = packet.dmxData
    led1 = (data[0], data[1], data[2])
    led2 = (data[3], data[4], data[5])

    sdk.set_led_colors_buffer_by_device_index(device2, {148: led1, 149: led2 })
    sdk.set_led_colors_flush_buffer()



devices = sdk.get_device_count()
print(devices)

i = 0
while i < devices:
    print(sdk.get_device_info(i))
    i += 1
    if i == devices:
      break

