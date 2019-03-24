#!/usr/bin/python3
import reader
import json
import sqlite3
import time
import statistics

# Read configuration
with open('/home/pi/EnergyMonitor/config.json') as json_data:
    config = json.load(json_data)

# Settings
loginterval = 60 # log interval in seconds
channels = [0,1,2,3]

# Set worker variables
prevtimestamp = [0.0,0.0,0.0,0.0]
timestamp = 0.0
r = reader.Reader(config)

# Infinite loop
while(True):
    try:
        nextlog = (time.time() // loginterval + 1) * loginterval

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
        conn = sqlite3.connect(config["Database"])
        c = conn.cursor()
        sql = "INSERT INTO ReadingData VALUES ({0},{1},{2},{3},{4},{5},{6},{7},NULL)"
        for channel in channels:
            c.execute(sql.format(nextlog,channel,totalWh[channel],min(valuesW[channel]),max(valuesW[channel]),statistics.mean(valuesW[channel]),statistics.stdev(valuesW[channel]),len(valuesW[channel])))
            print("{0}: {1}: totalWh: {2}".format(nextlog,channel,totalWh[channel]))
            print("{0}: {1}: minW: {2}".format(nextlog,channel,min(valuesW[channel])))
            print("{0}: {1}: maxW: {2}".format(nextlog,channel,max(valuesW[channel])))
            print("{0}: {1}: avgW: {2}".format(nextlog,channel,statistics.mean(valuesW[channel])))
            print("{0}: {1}: stdevW: {2}".format(nextlog,channel,statistics.stdev(valuesW[channel])))
            print("{0}: {1}: count: {2}".format(nextlog,channel,len(valuesW[channel])))
        conn.commit()
        conn.close()
    except Exception as e:
        print("An error occurred:", e)
