#!/bin/sh
# launcher.sh

cd ~pi/mjpg-streamer/mjpg-streamer-experimental
export LD_LIBRARY_PATH=.
./mjpg_streamer -i "input_uvc.so -d /dev/video1 -r 424x240 -f 30" -o "output_http.so -p 8080 -w ./www" &
./mjpg_streamer -i "input_uvc.so -d /dev/video2 -r 424x240 -f 30" -o "output_http.so -p 8081 -w ./www" &

cd ~pi/CORE2016-VISION
sudo python main.py
cd /
