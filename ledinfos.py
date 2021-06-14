from cuesdk import CueSdk


sdk = CueSdk()
sdk.connect()


device_count = sdk.get_device_count()

for device_index in range(device_count):
    info_Led = sdk.get_led_positions_by_device_index(device_index)
    info_device = sdk.get_device_info(device_index)
    print(device_index)
    print(info_device)
    print(info_Led)
    for led in info_Led.keys():
        print(led.value)
