from cuesdk import CueSdk


sdk = CueSdk()
sdk.connect()


device_count = sdk.get_device_count() - 1

i = 0
while i < device_count:
    info_Led = sdk.get_led_positions_by_device_index(i)
    info_device = sdk.get_device_info(i)
    print(i)
    print(info_device)
    print(info_Led)
    i += 1
    if i == device_count:
        break

