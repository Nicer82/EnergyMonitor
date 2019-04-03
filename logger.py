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

# Settings
channels = [0,1,2,3]

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
            for chan in channels:
                channelKey = "Channel{0}".format(chan)
                reader.readChannel(channel=chan,
                                   ampFactor=config["Logger"][channelKey]["AmpFactor"],
                                   ampExponent=config["Logger"][channelKey]["AmpExponent"],
                                   ampMinimum=config["Logger"][channelKey]["AmpMinimum"])
                power = reader.lastPower()
                timestamp = reader.lastStart()

                # calculate statistics, exclude the first measurement
                if(prevtimestamp[channel] > 0.0):
                    totalWh[channel] = totalWh[channel]+(power*(timestamp-prevtimestamp[channel])/3600)
                    valuesW[channel].append(power)

                # save last measurement timestamp for the channel
                prevtimestamp[channel] = timestamp

            # stop measuring if next log timestamp is reached
            if(timestamp >= logEnd):
                break

        # output data when something is collected
        conn = sqlite3.connect(config["Logger"]["Database"])
        c = conn.cursor()
        sql = "INSERT INTO ReadingData VALUES ({0},{1},{2},{3},{4},{5},{6},{7},NULL)"
        
        for chan in channels:
            c.execute(sql.format(logStart,chan,totalWh[channel],min(valuesW[channel]),max(valuesW[channel]),statistics.mean(valuesW[channel]),statistics.stdev(valuesW[channel]),len(valuesW[channel])))
        
        conn.commit()
        conn.close()
    except Exception as e:
        logging.exception("Exception occurred, waiting 10 seconds before continueing");
        
        # Reset reader object
        reader = CurrentReader(voltage=config["Logger"]["Voltage"])
        
        # Wait 10 seconds to avoid flooding the error log too much
        time.sleep(10)
