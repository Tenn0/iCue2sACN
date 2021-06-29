# iCue2sACN *WIP*

Corsair iCue Devices are nice, but theres no sACN function for iCue (yet). Since I like controlling all my devices via 1 protocol to sync them all, i decided to make a
custom iCue plugin to solve this. 
Im still working on a few things. Thanks to @not-matt the code should work for many devices, I can only confirm it works with Corsair K55 Keyboard, M65 Pro RGB Mouse, H100i Platinum RGB AiO Cooler and Lighting Node Core with 3 SP120 Plugged in.
For Smart Home purposes im going to add a bit mqtt, to have a switch available to toggle the magic show between sACN and iCUE. At some time, im going to add the possibility to disable every device by itself, but i need some time to do it. 

To use it, install via pip the packages cuesdk and sacn. Then run main.py






For one possible source of sACN, have a look at the ledfx project, which brings leds to live with music: https://ledfx.app/

