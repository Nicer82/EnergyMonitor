#!/usr/bin/python3
# -------------------------------------------------------------------------
# Program: Script to continuously read out the local SQLite DB, upload
#          the data in a remote MySQL DB and clean up the local SQLite DB.
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
import mysql.connector
import sqlite3
import json
import time
import socket
from datetime import datetime

# Read configuration
with open('/home/pi/EnergyMonitor/config.json') as json_data:
    config = json.load(json_data)
    
logging.basicConfig(filename='/home/pi/EnergyMonitor/uploader.log', level=logging.ERROR, 
                    format='%(asctime)s %(levelname)s %(message)s')

nextVacuum = (time.time() // config["Uploader"]["VacuumInterval"] + 1) * config["Uploader"]["VacuumInterval"]


# Infinite loop
while(True):
    try:
        # Set up DB connections
        connServer = mysql.connector.connect(user=config["Uploader"]["User"],
                                             password=config["Uploader"]["Password"],
                                             host=config["Uploader"]["Host"],
                                             port=config["Uploader"]["Port"],
                                             database=config["Uploader"]["Database"])
        connServer.autocommit = False
        
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
            try:
                curServer.execute("INSERT INTO ReadingData VALUES ('{0}','{1}',{2},{3},{4},{5},{6},{7},{8},'{9}')".format(datetime.utcfromtimestamp(row['TimeStamp']),
                                                                                                                    socket.gethostname(),
                                                                                                                    row['Channel'],
                                                                                                                    row['ConsumptionWh'],
                                                                                                                    row['PowerMinW'],
                                                                                                                    row['PowerMaxW'],
                                                                                                                    row['PowerAvgW'],
                                                                                                                    row['PowerStDevW'],
                                                                                                                    row['Measurements'],
                                                                                                                    datetime.utcfromtimestamp(uploadedTimeStamp)))
            # Ignore duplicate key exceptions, since they are most likely because the script was terminated unorthodox previously.
            except mysql.connector.IntegrityError as err:
                pass
            
            curLocal.execute("UPDATE ReadingData SET UploadedTimeStamp = {0} WHERE Timestamp = {1} AND Channel = {2}".format(uploadedTimeStamp,
                                                                                                                             row['TimeStamp'],
                                                                                                                             row['Channel']))
            
        # Remove data from local DB
        curLocal.execute("DELETE FROM ReadingData WHERE UploadedTimeStamp IS NOT NULL AND Timestamp < {0}".format(uploadedTimeStamp - (config["Uploader"]["LocalDataKeepDays"]*24*3600)))
        
        # Close the server DB
        connServer.commit()
        connServer.close()

        # Vacuum the local db if next time is reached.
        if(time.time() >= nextVacuum):
            curLocal.execute("VACUUM;")
            nextVacuum = (time.time() // config["Uploader"]["VacuumInterval"] + 1) * config["Uploader"]["VacuumInterval"]

        # Close the local DB
        connLocal.commit()
        connLocal.close() 
           
    except Exception as e:
        msg = ("An error occurred: {0}".format(e))
        print(msg)
        logging.error(e);
    finally:
        # Wait x seconds to upload next set of data
        time.sleep(config["Uploader"]["UploadInterval"])
