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
import logging
from datetime import datetime

# Read configuration
with open('/home/pi/EnergyMonitor/config.json') as json_data:
    config = json.load(json_data)
    
# Create a log file per day
logFileName = "/home/pi/EnergyMonitor/uploader_{0}.log".format(datetime.now().strftime("%Y%m%d_%H%M%S"))
logging.basicConfig(filename=logFileName, 
                    level=logging.ERROR, 
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
        
        connLocal = sqlite3.connect(config["Collector"]["Database"])
        connLocal.row_factory = sqlite3.Row

        # Worker variables
        uploadedTimeStamp = time.time()
        curServer = connServer.cursor()
        curLocal = connLocal.cursor()
        curLocal.execute("SELECT TimeStamp,Channel,Power FROM ReadingData WHERE Uploaded IS NULL")
        rows = curLocal.fetchall()
        
        # Loop through rows from local DB and insert them into the server DB
        for row in rows:
            try:
                curServer.execute("INSERT INTO ReadingData (TimeStamp,Device,Channel,Power,Uploaded) VALUES ('{0}','{1}',{2},{3},'{4}'".format(
                                                            datetime.utcfromtimestamp(row['TimeStamp']),
                                                            socket.gethostname(),
                                                            row['Channel'],
                                                            row['Power'],
                                                            datetime.utcfromtimestamp(uploadedTimeStamp)))
            # Ignore duplicate key exceptions, since they are most likely because the script was terminated unorthodox previously.
            except mysql.connector.IntegrityError as err:
                pass
            
            curLocal.execute("UPDATE ReadingData SET UploadedTimeStamp = {0} WHERE Timestamp = {1} AND Channel = {2}".format(uploadedTimeStamp,
                                                                                                                             row['TimeStamp'],
                                                                                                                             row['Channel']))
            
        # Remove data from local DB
        curLocal.execute("DELETE FROM ReadingData WHERE Uploaded IS NOT NULL AND Timestamp < {0}".format(uploadedTimeStamp - config["Uploader"]["LocalDataKeepInterval"]))
        
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
        print(e)
        logging.exception("Exception occurred")
    finally:
        # Wait x seconds to upload next set of data
        time.sleep(config["Uploader"]["UploadInterval"])
