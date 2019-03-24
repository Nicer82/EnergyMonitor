#import mysql.connector
import sqlite3
import json

# Read configuration
with open('/home/pi/EnergyMonitor/config.json') as json_data:
    config = json.load(json_data)

# Set up DB connection    
#connServer = mysql.connector.connect(user='EnergyMonitor', password='Energy4All!',
#                              host='192.168.1.2',
#                              database='EnergyMonitor')
connLocal = sqlite3.connect(config["Database"])
connLocal.row_factory = sqlite3.Row

curLocal = connLocal.cursor()
curLocal.execute("SELECT TimeStamp,Channel,ConsumptionWh,PowerMinW,PowerMaxW,PowerAvgW,PowerStDevW,Measurements FROM ReadingData WHERE UploadedTimeStamp IS NULL")

for row in curLocal:
  print(r['TimeStamp'],r['Channel'])
    
connLocal.close()
#connServer.close()
