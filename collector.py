import threading
import json
import time
import statistics
import logging
import emlib
from queue import Queue
from datetime import datetime

def postStates():
    while(not statePostQueue.empty()):
        jsondata = statePostQueue.get()
    
        while(jsondata):
            try:
                jsondata = statePostQueue.get()
                emlib.run_process('curl -H "Content-Type: application/json" -X PUT http://{}/state/{} -d\'{}\''.format(config["Collector"]["StateDevice"],jsondata['point'],json.dumps(jsondata)))
                jsondata = None
            except Exception as e:
                logging.exception("Failed to post state to the API: {}".format(e))
                time.sleep(5) # wait 5 seconds after an error to not overwhelm the attempts

# Read configuration
with open('config.json') as json_data:
    config = json.load(json_data)
    channels = []
    for i in range(config["Collector"]["Phases"]):
        channels.append(i*2)
        channels.append(i*2+1)
        
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
            #print("Channel {} before normalize: Reads: {}, Min: {}, Max: {}".format(i,len(data[i]),min(data[i]),max(data[i])))
            data[i] = emlib.normalize(data[i])
            #print("Channel {} after normalize: Reads: {}, Min: {}, Max: {}".format(i,len(data[i]),min(data[i]),max(data[i])))

        ### Calculate the power
        power = []
        voltage = []
        current = []
        jsondata = {}
        jsondata['point'] = config["Collector"]["Point"]
        jsondata['time'] = time.time()
        
        for li in range(config["Collector"]["Phases"]):
            powerdata = []                            
            ci = li*2
            vi = ci+1

            for reading in range(len(data[ci])):
                powerdata.append(data[ci][reading] * data[vi][reading])

            phase_power = statistics.mean(powerdata)*config["Collector"]["CalibrationFactor_Power"]
            power.append(phase_power)
            phase_voltage = emlib.rootmeansquare(data[vi])*config["Collector"]["CalibrationFactor_Voltage"]
            voltage.append(phase_voltage)
            phase_current = phase_power / phase_voltage
            current.append(phase_current)
            
            jsondata['l{}_current'.format(li+1)] = round(phase_current,3)
            jsondata['l{}_voltage'.format(li+1)] = round(phase_voltage,1)
            jsondata['l{}_power'.format(li+1)] = round(phase_power,4)

            #print("L{}: Current: {} A, Voltage: {} V, Power: {} W".format(li+1,round(current[li],3),round(voltage[li],1), round(power[li])))

        #print("Total: Current: {} A, Voltage: {} V, Power: {} W".format(round(sum(current),3),round(statistics.mean(voltage),1),round(sum(power))))
        
        jsondata['total_current'] = round(sum(current),3)
        jsondata['total_voltage'] = round(statistics.mean(voltage),1)
        jsondata['total_power'] = round(sum(power))
        
        # post the new state to the state device
        perfstart = time.perf_counter()
        statePostQueue.put(jsondata)
        if(not statePostThread or not statePostThread.is_alive()):
            statePostThread = threading.Thread(target=postStates)
            statePostThread.start()
        print("Start postStates in {} ms".format((time.perf_counter()-perfstart)*1000))
        
    except Exception as e:
        print(e)
        logging.exception("Exception occurred, waiting 10 seconds before continueing")

        # Wait 10 seconds to avoid flooding the error log too much
        time.sleep(10)

        # Reset the reader
        reader = emlib.AdcReader()
