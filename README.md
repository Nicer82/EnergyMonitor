# Monitoring Energy with your Raspberry Pi

The centerpiece of the design is an MCP3208 analog-to-digital controller, which used SPI to communicate with the RPi.

You will need a device or service running a MySQL database to store the volumes measured by the Energymonitor.

on the RPI, two pieces of software are running:
- collector.py: reads out the MCP3208 continuously and uploads the current state to:
- API/state.py: a RESTful API webservice using Flask that can return the last state, calculates the volume and uploads the volume to a MySQL database

## RPI Installation instructions
Tested with a Raspberry Pi Model 3B+. Should work on other RPi's as well.
### Raspbian setup
1. Download the latest image of Raspbian Lite, available at raspberrypi.org/downloads
2. Flash the image to a fresh micro SD card (I used balenaEtcher)
3. Plug the SD card into the raspberry PI together with a keyboard, screen and power
4. Wait for Raspbian to do its initial configuration. Once you get to the login prompt, log in with user 'pi', password 'raspbian'.
5. Open the Raspbian config tool with 'sudo raspi-config'
6. The following stuff depends on your preferences and type of Raspberry PI, but you will probably want to perform some basic setup like:
    - change the default password
  - set your own hostname
  - set your wifi settings (not necessary if you are using an UTP, connection)
  - set localisation options as preferred
  - set interfacing options
      - enable SSH
      - enable SPI (Required to be able to read out the MCP3208 chip!)
 7. You can set a static IP to the PI so your device is easier to find. I personally prefer to set a reserved IP for the MAC-address of the PI into my DHCP server.
 8. Exit the Raspbian config tool and reboot. From this point on, if you enabled SSH, you can disconnect the keyboard and screen and access the pi using SSH from another computer.
 9. Update the system packages with 'sudo apt-get update'

### Python 3
This is probably already installed.  If not, use sudo apt-get install python3 
### SpiDev module
sudo pip install spidev
### MySQL module
sudo pip3 install mysql-connector-python
### The source code of this project
#### Config file
Configuration is stored in the config.json file. There is a section for the collector and one for the Api.
### Setting up the API webservice (lighttpd webserver)

## MySQL DB setup instructions

