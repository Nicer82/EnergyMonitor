#!/usr/bin/python

import Adafruit_ADS1x15
import sqlite3
import datetime
import json
import functions
import threading

dt = datetime.datetime.now()
print("===== sampler.py starting at ", dt.isoformat())

#Read configuration
try:
    with open('./settings.json') as json_data:
        config = json.load(json_data)
#        print("Configuration read")
except IOError as e:
  print("Unable to open configuration file:", e)
  exit()
    
# Create an ADS1115 ADC (16-bit) instance.
adc = Adafruit_ADS1x15.ADS1115()

try:
    conn = sqlite3.connect(config["Database"])
#    print('Connected to database.')
except Exception as e:
    print("Unable to open database: ", e)
    exit()

# Read channels 0 - 3
amps0 = functions.readAmps( adc, 0, config)
amps1 = functions.readAmps( adc, 1, config)
amps2 = functions.readAmps( adc, 2, config)
amps3 = functions.readAmps( adc, 3, config)

#Save to the database
#try:
#    c = conn.cursor()
#    dt = datetime.datetime.now()
#    sql = "INSERT INTO ReadingData (TimeStamp, Channel, Current, TransmitDate) VALUES ('{0}', {1}, {2}, NULL)".format( dt.isoformat(), 0, amps0)
#    print( "Saving to database" )
#    c.execute(sql)
#    conn.commit()
#except sqlite3.Error as e:
#    print("Error writing to database: ", e)
#    exit()
    
#conn.close()
#print("Database closed")
print("Total Consumption:",(amps0+amps1+amps2)*240)
print("Total Production :",(amps3)*235)
dt = datetime.datetime.now()
print("===== sampler.py exiting at ", dt.isoformat())


