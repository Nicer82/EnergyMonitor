#!/usr/bin/python
import reader
import json

#Read configuration
try:
    with open('./settings.json') as json_data:
        config = json.load(json_data)
except IOError as e:
  print("Unable to open configuration file:", e)
  exit()
  
r = reader.Reader(config)
r.read()
print("Current:",r.getLastCurrent())
print("Power:",r.getLastPower())
