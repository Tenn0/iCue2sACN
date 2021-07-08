pyinstaller -i logo.ico -D -n "iCUE2sACN" ./src/main.py
git clone https://github.com/CorsairOfficial/cue-sdk-python 
robocopy ./cue-sdk-python/cuesdk/ ./dist/iCUE2sACN/cuesdk -E