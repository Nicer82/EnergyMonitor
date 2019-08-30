# Monitoring Energy with your Raspberry Pi
First of all: a big thank you to the guys at OpenEnergyMonitor, Almost all of the knowledge and information is comming from their very informative website https://learn.openenergymonitor.org. I would strongly encourage you to take your time and learn before you start building on this project.

The strength of this project is that you can combine multiple devices and centralize all information in one database. A big advantage is also that no data is written onto the SD cards of the RPI devices. As we all know, these wear out fast with heavy writing so the device would fail quite fast. Instead, all data is kept in memory and only made persistent in a centralized MySQL Database.

The centerpiece of the design is an MCP3208 analog-to-digital converter chip, which uses SPI to communicate with the RPi.
You will need a device or service running a MySQL database to store the volumes measured by the Energymonitor.
On the RPi, two pieces of software are running:
- collector.py: reads out the MCP3208 continuously and uploads the current state to:
- API/state.py: a RESTful API webservice using Flask that can return the last state, calculates the volume and uploads the volume to a MySQL database

The MySQL database can run on any device or even in the cloud if you like. I personally used a MariaDB instance on my Synology server, simply because I already had that one. The end point of this project is this MySQL Database containing all the measurd data. A front-end app to visualize and consult that data goes beyond the scope of this project and depends on what you are actually measuring.
## 1. Hardware setup
The Energy Monitor can be ran in two modes:
- with voltage measurement: in this case you can also determine the flow direction of the current. 
- without voltage measurement, using the voltage measurement form another EnergyMonitor device. Current and power will always be positive using this mode

If current flow direction is not important for you (the flow direction is only oen direction), You could skip the whole measurement of the voltage and hardcode the average voltage for your network in the VoltageService class, but because voltages can fluctuate a lot, it is way more accurate to use the actual voltage for power calculations.
### 1.1 RPi power source
I learned during this project that the power source you are using to power the RPi is very important to output a stable DC voltage (5-5.3V) that can deliver enough amps (+3A). The more stable this is, the more accurate your readings will be. I disassembled an IKEA-branded USB charger, which works very well and gave me the most accurate results.
### 1.2 Wiring schema for a current measurement channel
Below wiring schemes is what I used. If you are measuring multiple wires, you will need to multiply these circuits and connect them to different channels of the MCP3208.
#### 1.2.1 Component list
TBD
#### 1.2.2 Schema
TBD
### 1.3 Wiring schema for a voltage measurement channel
Below wiring schemes is what I used. If you are measuring multiple wires, you will need to multiply these circuits and connect them to different channels of the MCP3208.
#### 1.3.1 Component list
TBD
#### 1.3.2 Schema
TBD
## 2. RPi Installation instructions
Tested with a Raspberry Pi Model 3B+. Should work on other RPi's as well.
### 2.1 Raspbian setup
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

### 2.2 Install dependent software
- sudo apt-get -y install python3 python3-pip git screen lighttpd
- sudo pip3 install spidev mysql-connector-python flask flask_restful
### 2.3 Install the source code of this project
- git clone https://github.com/Nicer82/EnergyMonitor
- cd EnergyMonitor
#### 2.3.1 Config file
Configuration is stored in the config.json file. There is a section for the collector and one for the Api. Edit the settings according to your needs
- open the file with 'sudo nano config.json'
- Edit the settings according to your setup:
    - Collector
        - Point: logical name for the point you are measuring, for instance: Mains, SolarGarage,SolarHome, ...
        - SamplesPerWave: The number of samples you want to take from one sine wave (pos and neg). The higher this number, the more accurate the measurement is but the more CPU time is consumed. 60 is about the maximum for a RPI where the python code can stil catch up. (in a 50 Hz network, this is one sample per channel every 0.333 millisecond!)
        - WavesToRead: The number of sine waves you want to read for one state update. The higher this number, the more accurate the state will be, but the more time there will be between state updates. if set to 50, this means a state update every second (WavesToRead / Frequency = state update time in seconds)
        - Frequency: The Frequency in Hz for the electricity network. In Europe, this is 50, in North America this is 60.
        - CalibrationFactor_Power: The calibration factor for the power calculations. Compare the results of the monitor with an accurate power measurement device and increase this value when its too low, decrease when its too high. The used resistors, capacitors, RPi power shource and wiring might require you to adjust this parameter.
        - CalibrationFactor_Voltage: same as the above, but for the voltage results.
        - VoltageService: RESTful API service where you want to fetch the voltage from.
            - In case you run the monitor with voltage measurement, leave this empty and provide the VoltageChannels below for your wires.
            - In case you run the monitor without voltage measurement, fill in the state service url of the device that measures the voltage for your wires.
        - CurrentChannels: a list of the wires you are measuring the current for. Easiest is to name the wires according to their color. The channel is an integer value from 0-7, pointing the the channel index of the MCP3208.
        - VoltageChannels: a list of the wires you are measuring the voltage for. Shoudl only be filled in when you run the monitor with voltage measurement. Each measured current channel should have a corresponding voltage channel.
    - Api
        - Port: The TCP port on which the Restful API service should run to collect and report the last state.
        - VolumeDataSeconds: the time interval how frequent a VolumeData record should be written.
        - VolumeDbHost: Host name of the machine running the MySQL database to keep the VolumeData.
        - VolumeDbPort: TCP port where MySQL is running.
        - VolumeDbName: Database name that contains the VolumeData table.
        - VolumeDbUser: MySQL Username.
        - VolumeDbPassword: MySQL Password.
#### 2.3.2 Setting up the API webservice (lighttpd webserver)
- Open the lighttpd config file
```
sudo nano /etc/lighttpd/lighttpd.conf
```
- Add these lines to the config file and save it:
TBD
- Allow execution on state.py with 'sudo chmod 775 /home/pi/EnergyMonitor/API/state.py'
- Allow writing the lighttpd cache location with 'sudo chmod 775 /var/cache/lighttpd'
- Restart the lighttpd service with 'sudo systemctl restart lighttpd'
- Validate a succesful start with 'systemctl status lighttpd.service'

#### 2.3.3 Set collector.py to start at boot
You need to add a startup command to the /etc/rc.local file to run the collector at boot. I prefer to run it using screen, so you can resume the screen afterwards in case of issues.
- sudo nano /etc/rc.local
- TBD
## 3. MySQL DB setup instructions
To create the required table(s) on your MySQL Database, you can use the script db.sql
