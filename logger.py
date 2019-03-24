#!/usr/bin/python
import reader
import json
import sqlite3
import time

# Read configuration
with open('./config.json') as json_data:
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
        minW = [99999,99999,99999,99999]
        maxW = [0,0,0,0]
        count = [0,0,0,0]

        while(True):
            # collect data for all channels
            for channel in channels:
                r.read(channel)
                valueW = r.getLastPower()
                timestamp = r.getLastStart()

                # calculate statistics, exclude the first measurement
                if(prevtimestamp[channel] > 0.0):
                    totalWh[channel] = totalWh[channel]+(valueW*(timestamp-prevtimestamp[channel])/3600)
                    minW[channel] = min(minW[channel],valueW)
                    maxW[channel] = max(maxW[channel],valueW)
                    count[channel] = count[channel]+1

                # save last measurement timestamp for the channel
                prevtimestamp[channel] = timestamp

            # stop measuring if next log timestamp is reached
            if(timestamp >= nextlog):
                break

        #output data when something is collected
        for channel in channels:
            print("{0}: {1}: totalWh: {2}".format(nextlog,channel,totalWh[channel]))
            print("{0}: {1}: minW: {2}".format(nextlog,channel,minW[channel]))
            print("{0}: {1}: maxW: {2}".format(nextlog,channel,maxW[channel]))
            print("{0}: {1}: count: {2}".format(nextlog,channel,count[channel]))
        #conn = sqlite3.connect(config["Database"])
        #c = conn.cursor()
        #sql = "INSERT INTO ReadingData VALUES ({0},{1},{2},{3})"
    except Exception as e:
        print("An error occurred:", e)
    

# Read the channels
#r.read(0)
#c.execute(sql.format(r.getLastStart(),0,r.getLastPower(),'NULL'))
#r.read(1)
#c.execute(sql.format(r.getLastStart(),1,r.getLastPower(),'NULL'))
#r.read(2)
#c.execute(sql.format(r.getLastStart(),2,r.getLastPower(),'NULL'))
#r.read(3)
#print(r.getLastPower())
#c.execute(sql.format(r.getLastStart(),3,r.getLastPower(),'NULL'))

# Close the DB
#conn.commit()
#conn.close()

    # Wait 5 seconds
#    time.sleep(config["LoopWaitSeconds"])
