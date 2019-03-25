##Monitoring Energy with your Raspberry Pi

The centerpiece of the design is an ADC1115 analog-to-digital controller, which used I2C to communicate with the RPi.

The software consists of two scripts that should run continuously on your RPi and that you probably want to start automatically from /etc/rc.local or through another way.

1. logger.py: A python script that reads out the current sensors and saves the reading data to a local database on the RPi
2. uploader.py: A python script that uploads the reading data to a remote MySQL DB and cleans up the local DB

![Here is a photo of what the prototype looks like](./HomeEnergyPrototype.jpg)

##Prerequisites

A Raspberry Pi.  I did my development on a Raspberry Pi Model 3B+. Should work on other RPi's as well.

- Python 3 - This is probably already installed.  If not, use sudo apt-get install python3 
- SQLite 3 - Install this using sudo apt-get install sqlite3 
- ADS1115 module - sudo pip3 install <TODO>
- MySQL module - sudo pip3 install <TODO>

##Configuration
Configuration is stored in the config.json file. There is a section for every python script.

- test
  - test
{
  "Reader":
  {
    "Voltage": 240, --> average voltage of the measured installation
    "Substractor": 3.4, --> the value the sensors pick up when no current is flowing. This corrects hardware offsets. Can be positive or negative.
    "Factor": 0.0152, --> depending on the type of sensors, resistors you use, a different multiplication needs to be done to go from the read value to the actual Amps. The right value for your implementation should be determined by testing.
    "Gain": 1, --> ADS1115 Gain value
    "DataRate": 860, --> ADS1115 Data rate value
    "ReadTime": 0.25 --> Time in seconds you want to read the sine wave from the sensor
  },
  "Logger":
  {
    "Database": "/home/pi/EnergyMonitor/EnergyMonitor.db", --> Location of the local SQLite DB
    "LogInterval": 60 --> A record per channel per x seconds is created in the ReadingData table
  },
  "Uploader":
  {
    "Host": "mySqlServer", --> Location of the remote MySQL DB
    "Port": 3307, --> Port of the remote MySQL DB
    "Database": "EnergyMonitor", --> DB Name of the remote MySQL DB
    "User": "EnergyMonitor", --> Credentials to connect to the remote MySQL DB
    "Password": "MVmIVKdWl69QQMjR", --> Credentials to connect to the remote MySQL DB
    "UploadInterval": 10, --> Time in seconds to check for records in the local DB to upload.
    "LocalDataKeepDays": 1 --> Number of days of data you want to keep in the local DB before erasing it.
  }
}

##logger.py

<TODO>
  
##uploader.py

<TODO>
