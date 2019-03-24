#!/usr/bin/python
import reader
import json
import sqlite3
import time

# Read configuration
with open('./config.json') as json_data:
    config = json.load(json_data)

# Infinite loop
#while True:
#try:
# Set worker variables and open the DB
#conn = sqlite3.connect(config["Database"])
#c = conn.cursor()
#sql = "INSERT INTO ReadingData VALUES ({0},{1},{2},{3})"
r = reader.Reader(config)

# Read the channels
#r.read(0)
#c.execute(sql.format(r.getLastStart(),0,r.getLastPower(),'NULL'))
#r.read(1)
#c.execute(sql.format(r.getLastStart(),1,r.getLastPower(),'NULL'))
#r.read(2)
#c.execute(sql.format(r.getLastStart(),2,r.getLastPower(),'NULL'))
r.read(3)
#c.execute(sql.format(r.getLastStart(),3,r.getLastPower(),'NULL'))

# Close the DB
#conn.commit()
#conn.close()

    # Wait 5 seconds
#    time.sleep(config["LoopWaitSeconds"])
#except Exception as e:
#    print("An error occurred:", e)
