# RaspberryRadio
Repo to upload code for RaspberryRadio

Small project I did with a Raspbery Pi and PiFmRds to:
- Scan network for a Raspberry Pi and then connect to it
- Transfer a .wav file from my laptop the the Pi
- Broadcast the given file at a given FM frequency for a given time
using python.

Requires: 
- Laptop (project was tested on my Mac) 
- A headless (can login over LAN using ssh without logging in on the Pi itself) Raspberry Pi running linux
- Piece of wire on GPIO 4 to act as an antenna (optional, the pin itself can act as a really tiny antenna)

Simply run combined .py after all dependencies are setup and your computer and Pi are on the same network. 
Relevent libraries are in the import calls in the code itself.
