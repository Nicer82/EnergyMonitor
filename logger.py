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
import statistics
import logging

# Read configuration
with open('/home/pi/EnergyMonitor/config.json') as json_data:
    config = json.load(json_data)

# Create a log file per day
logFileName = "/home/pi/EnergyMonitor/logger_{0}.log".format(datetime.now().strftime("%Y%m%d"))
logging.basicConfig(filename=logFileName, 
                    level=logging.ERROR, 
                    format='%(asctime)s %(levelname)s %(message)s')

# Set worker variables
prevtimestamp = [0.0,0.0,0.0,0.0]
reader = CurrentReader(voltage=config["Logger"]["Voltage"])

# Infinite loop
while(True):
    try:
        # Reset statistics
        totalWh = [0,0,0,0]
        valuesW = [[],[],[],[]]

        logStart = (time.time() // config["Logger"]["LogInterval"]) * config["Logger"]["LogInterval"]
        logEnd = (logStart // config["Logger"]["LogInterval"] + 1) * config["Logger"]["LogInterval"]

        while(True):
            # collect data for all channels
            for chan in config["Logger"]["Channels"]:
                chanInt = int(chan)
                reader.readChannel(chan=chanInt,
                                   ampFactor=config["Logger"]["Channels"][chan]["AmpFactor"],
                                   ampExponent=config["Logger"]["Channels"][chan]["AmpExponent"],
                                   ampMinimum=config["Logger"]["Channels"][chan]["AmpMinimum"])
                power = reader.lastPower()
                timestamp = reader.lastStart()

                # calculate statistics, exclude the first measurement
                if(prevtimestamp[chanInt] > 0.0):
                    totalWh[chanInt] = totalWh[chanInt]+(power*(timestamp-prevtimestamp[chanInt])/3600)
                    valuesW[chanInt].append(power)

                # save last measurement timestamp for the channel
                prevtimestamp[chanInt] = timestamp

            # stop measuring if next log timestamp is reached
            if(timestamp >= logEnd):
                break

        # output data when something is collected
        conn = sqlite3.connect(config["Logger"]["Database"])
        c = conn.cursor()
        sql = "INSERT INTO ReadingData VALUES ({0},{1},{2},{3},{4},{5},{6},{7},NULL)"
        
        for chan in config["Logger"]["Channels"]:
            chanInt = int(chan)
            c.execute(sql.format(logStart,
                                 chanInt,
                                 totalWh[chanInt],
                                 min(valuesW[chanInt]),
                                 max(valuesW[chanInt]),
                                 statistics.mean(valuesW[chanInt]),
                                 statistics.stdev(valuesW[chanInt]),
                                 len(valuesW[chanInt])))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)
        
        logging.exception("Exception occurred, waiting 10 seconds before continueing")
        
        # Reset reader object
        reader = CurrentReader(voltage=config["Logger"]["Voltage"])
        
        # Wait 10 seconds to avoid flooding the error log too much
        time.sleep(10)
