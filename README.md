# iCue2sACN *WIP*

Corsair iCue Devices are nice, but theres no sACN function for iCue (yet). Since I like controlling all my devices via 1 protocol to sync them all, i decided to make a
custom iCue plugin to solve this. 
Im still working on a few things. Thanks to @not-matt the code should work for many devices, I can only confirm it works with Corsair K55 Keyboard, M65 Pro RGB Mouse, H100i Platinum RGB AiO Cooler and Lighting Node Core with 3 SP120 Plugged in.
For Smart Home purposes im going to add a bit mqtt, to have a switch available to toggle the magic show between sACN and iCUE. At some time, im going to add the possibility to disable every device by itself, but i need some time to do it. 

To use it, install via pip the packages cuesdk and sacn. Then run main.py or follow instructions below.

In this branch im going to work on adding mqtt, including: Set layer_priority (works, needs a bit of love), request exclusive control (works), switch between sACN and iCUE as effect source (works), static lighting (works), auto discovery for Home Assistant (works) and brightness control in manual mode (working on it).

Also new in this branch is a build script! Clone this repo for this example into C://, go to C://iCUE2sACN and execute build.bat. Also, theres a VSCode build task available: F1, Tasks:Run Task, build windows exe. No matter which path you follow, you can copy the whole folder C://iCUE2sACN/dist/iCUE2sACN to any location you want and execute iCUE2sACN.exe. Then edit mqtt.json, according to you liking. Please note, if the file is not valid json, it will get recreated at next startup! Then start the exe again and adjust your sACN sender to your liking!
If MQTT is enabled, the universes for your devices will get dumped to the base topic you specified. Also, they will get dumped to the console.


For one possible source of sACN, have a look at the ledfx project, which brings leds to live with music: https://ledfx.app/

