#!/usr/bin/python3
# -------------------------------------------------------------------------
# Program: Script to continuously read out the current sensors and save
#          the results in a local SQLite DB.
#          This script should be setup to run at boot of the 
#          monitoring device.
#
# Copyright (C) 2019 Bjorn Douchy
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License at https://www.gnu.org/licenses
#    for more details.
# -------------------------------------------------------------------------
from currentreader import CurrentReader
from datetime import datetime
import json
import sqlite3
import time
import logging

# Read configuration
with open('/home/pi/EnergyMonitor/config.json') as json_data:
    config = json.load(json_data)

# Create a new log file per start
logFileName = "/home/pi/EnergyMonitor/collector_{0}.log".format(datetime.now().strftime("%Y%m%d_%H%M%S"))
logging.basicConfig(filename=logFileName, 
                    level=logging.ERROR, 
                    format='%(asctime)s %(levelname)s %(message)s')

# Create CurrentReader object
reader = CurrentReader(frequency=config["Collector"]["Frequency"])

nextSave = time.time()+config["Collector"]["SaveInterval"]
lastTimeStamp = (time.time() // config["Collector"]["ReadInterval"] * config["Collector"]["ReadInterval"])
lastTimeStamps = [lastTimeStamp,lastTimeStamp,lastTimeStamp,lastTimeStamp]
unsaved = []

# Infinite loop
while(True)
    try:
        for chan in config["Collector"]["Channels"]:
            chanInt = int(chan)
            reader.readChannel(chan=chanInt,
                               ampFactor=config["Collector"]["Channels"][chan]["AmpFactor"],
                               ampExponent=config["Collector"]["Channels"][chan]["AmpExponent"],
                               ampMinimum=config["Collector"]["Channels"][chan]["AmpMinimum"])
            power = reader.lastCurrent()*config["Collector"]["Voltage"]
            
            while(lastTimeStamps[chanInt] < reader.lastStart())
                unsaved.append([lastTimeStamps[chanInt], chanInt, power])
                lastTimeStamps[chanInt] = lastTimeStamps[chanInt] + config["Collector"]["ReadInterval"]
        
        if(time.time() >= nextSave):
            conn = sqlite3.connect(config["Collector"]["Database"])
            c = conn.cursor()
            sql = "INSERT INTO ReadingData (TimeStamp,Channel,Power) VALUES ({0},{1},{2})"

            for unsavedrow in unsaved:
                c.execute(sql.format(unsavedrow[0],unsavedrow[1],unsavedrow[2]))

            conn.commit()
            conn.close()

            unsaved = []
    except Exception as e:
        print(e)
        logging.exception("Exception occurred, waiting 10 seconds before continueing")

        # Reset reader object
        reader = CurrentReader(frequency=config["Collector"]["Frequency"])

        # Wait 10 seconds to avoid flooding the error log too much
        time.sleep(10)
