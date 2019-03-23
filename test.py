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
r.read(0)
consphase1 = r.getLastPower()
r.read(1)
consphase2 = r.getLastPower()
r.read(2)
consphase3 = r.getlastPower()
r.read(3)
prod = r.getlastPower()

print("Total consumption :",consphase1+consphase2+consphase3)
print("Total production  :",prod)
