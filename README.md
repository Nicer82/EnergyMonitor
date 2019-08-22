# Monitoring Energy with your Raspberry Pi

The centerpiece of the design is an MCP3208 analog-to-digital controller, which used SPI to communicate with the RPi.

You will need a device or service running a MySQL database to store the volumes measured by the Energymonitor.

on the RPI, two pieces of software are running:
- collector.py: reads out the MCP3208 continuously and uploads the current state to:
- API/state.py: a RESTful API webservice using Flask that can return the last state, calculates the volume and uploads the volume to a MySQL database

## MySQL DB setup instructions

## RPI Installation instructions

Tested with a Raspberry Pi Model 3B+. Should work on other RPi's as well.

### Python 3 - This is probably already installed.  If not, use sudo apt-get install python3 
### SpiDev module - sudo pip install spidev
### MySQL module - sudo pip3 install mysql-connector-python
### The source code of this project
#### Config file

Configuration is stored in the config.json file. There is a section for the collector and one for the Api.

### Setting up the API webservice (lighttpd webserver)
