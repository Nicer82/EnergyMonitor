import mysql.connector
import sqlite3
import json
import time
import socket
from datetime import datetime

# Read configuration
with open('/home/pi/EnergyMonitor/config.json') as json_data:
    config = json.load(json_data)

# Infinite loop
while(True):
    try:
        # Set up DB connections
        connServer = mysql.connector.connect(user=config["Uploader"]["User"],
                                             password=config["Uploader"]["Password"],
                                             host=config["Uploader"]["Host"],
                                             port=config["Uploader"]["Port"],
                                             database=config["Uploader"]["Database"])
        connLocal = sqlite3.connect(config["Logger"]["Database"])
        connLocal.row_factory = sqlite3.Row

        # Worker variables
        uploadedTimeStamp = time.time()
        curServer = connServer.cursor()
        curLocal = connLocal.cursor()
        curLocal.execute("SELECT TimeStamp,Channel,ConsumptionWh,PowerMinW,PowerMaxW,PowerAvgW,PowerStDevW,Measurements FROM ReadingData WHERE UploadedTimeStamp IS NULL")
        rows = curLocal.fetchall()

        # Loop through rows from local DB and insert them into the server DB
        for row in rows:
            curServer.execute("INSERT INTO ReadingData VALUES ('{0}','{1}',{2},{3},{4},{5},{6},{7},{8},'{9}')".format(datetime.fromtimestamp(row['TimeStamp']),
                                                                                                                socket.gethostname(),
                                                                                                                row['Channel'],
                                                                                                                row['ConsumptionWh'],
                                                                                                                row['PowerMinW'],
                                                                                                                row['PowerMaxW'],
                                                                                                                row['PowerAvgW'],
                                                                                                                row['PowerStDevW'],
                                                                                                                row['Measurements'],
                                                                                                                datetime.fromtimestamp(uploadedTimeStamp)))
            curLocal.execute("UPDATE ReadingData SET UploadedTimeStamp = {0} WHERE Timestamp = {1} AND Channel = {2}".format(uploadedTimeStamp,
                                                                                                                             row['TimeStamp'],
                                                                                                                             row['Channel']))
            
        # Remove data from local DB
        curLocal.execute("DELETE FROM ReadingData WHERE Timestamp < {0}".format(uploadedTimeStamp - (config["Uploader"]["LocalDataKeepDays"]*24*3600)))
        
        # Close Databases
        connServer.commit()
        connServer.close()
        connLocal.commit()
        connLocal.close()    
    except Exception as e:
        print("An error occurred:", e)
    finally:
        # Wait x seconds to upload next set of data
        time.sleep(config["Uploader"]["UploadInterval"])
