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
import reader
import json
import sqlite3
import time
import statistics

# Read configuration
with open('/home/pi/EnergyMonitor/config.json') as json_data:
    config = json.load(json_data)

# Settings
channels = [0,1,2,3]

# Set worker variables
prevtimestamp = [0.0,0.0,0.0,0.0]
timestamp = 0.0
r = reader.Reader(config)

# Infinite loop
while(True):
    try:
        curlog = (time.time() // config["Logger"]["LogInterval"]) * config["Logger"]["LogInterval"]
        nextlog = (curlog // config["Logger"]["LogInterval"] + 1) * config["Logger"]["LogInterval"]

        # Reset statistics
        totalWh = [0,0,0,0]
        valuesW = [[],[],[],[]]

        while(True):
            # collect data for all channels
            for channel in channels:
                r.read(channel)
                valueW = r.getLastPower()
                timestamp = r.getLastStart()

                # calculate statistics, exclude the first measurement
                if(prevtimestamp[channel] > 0.0):
                    totalWh[channel] = totalWh[channel]+(valueW*(timestamp-prevtimestamp[channel])/3600)
                    valuesW[channel].append(valueW)

                # save last measurement timestamp for the channel
                prevtimestamp[channel] = timestamp

            # stop measuring if next log timestamp is reached
            if(timestamp >= nextlog):
                break

        # output data when something is collected
        conn = sqlite3.connect(config["Logger"]["Database"])
        c = conn.cursor()
        sql = "INSERT INTO ReadingData VALUES ({0},{1},{2},{3},{4},{5},{6},{7},NULL)"
        
        for channel in channels:
            c.execute(sql.format(curlog,channel,totalWh[channel],min(valuesW[channel]),max(valuesW[channel]),statistics.mean(valuesW[channel]),statistics.stdev(valuesW[channel]),len(valuesW[channel])))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print("An error occurred:", e)
