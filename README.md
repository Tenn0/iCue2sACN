# iCue2sACN *WIP*

Corsair iCue Devices are nice, but theres no sACN function for iCue (yet). Since I like controlling all my devices via 1 protocol to sync them all, i decided to make a
custom iCue plugin to solve this. 
Im still working on a few things. Thanks to @not-matt the code should work for many devices, I can only confirm it works with Corsair K55 Keyboard, M65 Pro RGB Mouse, H100i Platinum RGB AiO Cooler and Lighting Node Core with 3 SP120 Plugged in.
For Smart Home purposes im going to add a bit mqtt, to have a switch available to toggle the magic show between sACN and iCUE. At some time, im going to add the possibility to disable every device by itself, but i need some time to do it. 

To use it, install via pip the packages cuesdk and sacn. Then run main.py

In this branch im going to address the issue of iCUE spitting out the devices with changing device indecies, causing the programm to open them on different universes.
Currently (22.6.2021) I added the ability to read from a json file, i gotta need to implement saving the devices to this file next.




For one possible source of sACN, have a look at the ledfx project, which brings leds to live with music: https://ledfx.app/

