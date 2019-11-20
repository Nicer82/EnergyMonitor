#! /usr/bin/python3
import os
import threading
import socket
import json
import time
import statistics
import logging
import emlib
from queue import Queue
from datetime import datetime

def postStates():
    while(not statePostQueue.empty()):
        statePost = statePostQueue.get()
    
        while(statePost):
            try:
                # temp for debugging
                #print("POST: {}".format(statePost))
                #break;
            
                # Get the current IP
                ip = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
                emlib.run_process('curl -s -m 5 -H "Content-Type: application/json" -X PUT http://{}:{}/state/{} -d\'{}\''.format(ip, config["Api"]["Port"],statePost['point'],json.dumps(statePost)))
                statePost = None
            except Exception as e:
                logging.exception("Failed to post state to the API: {}".format(e))
                time.sleep(5) # wait 5 seconds after an error to not overwhelm the attempts

# Read configuration
with open(os.path.join(os.getcwd(),'config.json')) as json_data:
    config = json.load(json_data)
    channels = []
    currentidxs = {}
    voltageidxs = {}

    if(config["Collector"]["VoltageService"]):
        voltageService = emlib.VoltageService(url=config["Collector"]["VoltageService"],
                                              samplesperwave=config["Collector"]["SamplesPerWave"],
                                              wavestoread=config["Collector"]["WavesToRead"],
                                              calibrationfactor=config["Collector"]["CalibrationFactor_Voltage"])
    else:
        voltageService = None
    for wirecolor in config["Collector"]["CurrentChannels"]:
        # Add a current measurement channel for every phase (even channel numbers)
        channels.append(config["Collector"]["CurrentChannels"][wirecolor])
        currentidxs[wirecolor] = len(channels)-1
        
        # In case no voltage service is setup, we also need to measure the voltage
        # Always read the voltage of a phase directly after the current to avoid too much time between those reads.
        if(not voltageService): 
            channels.append(config["Collector"]["VoltageChannels"][wirecolor])
            voltageidxs[wirecolor] = len(channels)-1
    
# Create a new log file per start
logFileName = "collector_{0}.log".format(datetime.now().strftime("%Y%m%d_%H%M%S"))
logging.basicConfig(filename=logFileName, 
                    level=logging.ERROR, 
                    format='%(asctime)s %(levelname)s %(message)s')

# Create the reader object
reader = emlib.AdcReader()

# Create a Queue for posting the states to the state service
statePostQueue = Queue()
statePostThread = None

# Infinite loop
while(True):
    try:
        ### Read the channels
        data = reader.readSineWave(channels,config["Collector"]["SamplesPerWave"],config["Collector"]["WavesToRead"],config["Collector"]["Frequency"])

        ### Normalize the captured data
        for i in range(len(data)):
            data[i] = emlib.normalize(data[i])
        
        ### Calculate the power
        power = []
        voltage = []
        current = []
        jsondata = {}
        jsondata['point'] = config["Collector"]["Point"]
        jsondata['time'] = time.time()
        
        for wirecolor in config["Collector"]["CurrentChannels"]:
            powerdata = []                            

            if(voltageService):
                voltageData = voltageService.wireVoltageData(wirecolor, data[currentidxs[wirecolor]])
            else:
                voltageData = data[voltageidxs[wirecolor]]

            for reading in range(len(data[currentidxs[wirecolor]])):
                powerdata.append(data[currentidxs[wirecolor]][reading] * voltageData[reading])
            
            wirepower = statistics.mean(powerdata)*config["Collector"]["CalibrationFactor_Power"]
            
            if(voltageService):
                wirevoltage = voltageService.voltage[wirecolor]
                # In case we are not measuring voltage, we can't determine the current flow and power is always a positive number. 
                # We are assuming current only flows in one direction.
                # However for instance an inverter which is idle consumes a couple of watts, which would be counted as Supply but is actually Usage.
                # To at least not see this as Supply, omit power values lower then 10 Watt.
                if(wirepower < 10):
                    wirepower = 0
            else:
                wirevoltage = emlib.rootmeansquare(voltageData)*config["Collector"]["CalibrationFactor_Voltage"]
            
            wirecurrent = wirepower / wirevoltage
                
            power.append(wirepower)
            voltage.append(wirevoltage)
            current.append(wirecurrent)
            
            jsondata[wirecolor] = {}
            jsondata[wirecolor]['current'] = round(wirecurrent,3)
            jsondata[wirecolor]['voltage'] = round(wirevoltage,1)
            jsondata[wirecolor]['power'] = round(wirepower,4)

        jsondata['current'] = round(sum(current),3)
        jsondata['voltage'] = round(statistics.mean(voltage),1)
        jsondata['power'] = round(sum(power))
        
        # post the new state to the state device
        statePostQueue.put(jsondata.copy())
        if(not statePostThread or not statePostThread.is_alive()):
            statePostThread = threading.Thread(target=postStates)
            statePostThread.start()
        
    except Exception as e:
        # temp for debugging
        #raise 

        logging.exception("Exception occurred, waiting 10 seconds before continueing")

        # Wait 10 seconds to avoid flooding the error log too much
        time.sleep(10)

        # Reset the reader
        reader = emlib.AdcReader()
