import json
import time
import statistics
import math
import spidev
import logging
from datetime import datetime

def rootmeansquare(values):
    # RMS = SQUARE_ROOT((values[0]² + values[1]² + ... + values[n]²) / LENGTH(values))
    sumsquares = 0.0

    for value in values:
        sumsquares = sumsquares + (value)**2 

    if len(values) == 0:
        rms = 0.0
    else:
        rms = math.sqrt(float(sumsquares)/len(values))

    return rms

def normalize(values):
    avg = round(statistics.mean(values))

    # Substract the mean of every value to set the mean to 0
    for i in range(len(values)):
        values[i] -= avg
        
    return values

def readadc(channels,samplesperwave,wavestoread,frequency):
    data = []
    
    for i in channels:
        data.append([])
        
    start = time.perf_counter()
    nextRead = start

    for i in range(samplesperwave*wavestoread):
        nextRead += 1/(samplesperwave*frequency)

        # Read channels
        for ci in range(len(channels)):
            # Add a delay on the last channel to match timings. This is way more accurate than time.sleep() because it works up to the microsecond.
            if(ci == len(channels)-1):
                delay = max([0,round((nextRead-time.perf_counter())*1000000)]) 
            else:
                delay = 0

            response = spi.xfer2([6+((4&channels[ci])>>2),(3&channels[ci])<<6,0],2000000,delay)
            data[ci].append(((response[1] & 15) << 8) + response[2])

    end = time.perf_counter()

    #for i in range(len(data[0])):
    #    print("{};{}".format(data[0][i],data[1][i]))

    #print("Reads: {}, Performance: {} sps, Requested time: {} ms, Actual time: {} ms".format(len(data[0]),len(data[0])/(end-start),1000/AC_FREQUENCY*ADC_ACWAVESTOREAD,(end-start)*1000))
    
    return data

# Read configuration
with open('/home/pi/EnergyMonitor/config.json') as json_data:
    config = json.load(json_data)
    channels = []
    for i in range(config["Collector"]["Phases"]):
        channels.append(i*2)
        channels.append(i*2+1)
        
# Create a new log file per start
logFileName = "/home/pi/EnergyMonitor/collector_{0}.log".format(datetime.now().strftime("%Y%m%d_%H%M%S"))
logging.basicConfig(filename=logFileName, 
                    level=logging.ERROR, 
                    format='%(asctime)s %(levelname)s %(message)s')

# Create the SPI
spi = spidev.SpiDev()
spi.open(0,0)

lastread = time.perf_counter()

# Infinite loop
while(True):
    try:
        ### Read the channels
        data = readadc(channels,config["Collector"]["SamplesPerWave"],config["Collector"]["WavesToRead"],config["Collector"]["Frequency"])

        ### Normalize the captured data
        for i in range(len(data)):
            #print("Channel {} before normalize: Reads: {}, Min: {}, Max: {}".format(i,len(data[i]),min(data[i]),max(data[i])))
            data[i] = normalize(data[i])
            #print("Channel {} after normalize: Reads: {}, Min: {}, Max: {}".format(i,len(data[i]),min(data[i]),max(data[i])))

        ### Calculate the power
        power = []
        voltage = []
        current = []
        jsondata = {}
        jsondata['point'] = config["Collector"]["Point"]
        jsondata['time'] = time.time()
        jsondata['phases'] = []
        
        for li in range(config["Collector"]["Phases"]):
            powerdata = []                            
            ci = li*2
            vi = ci+1

            for reading in range(len(data[ci])):
                powerdata.append(data[ci][reading] * data[vi][reading])

            phase_power = statistics.mean(powerdata)*config["Collector"]["CalibrationFactor_Power"]
            power.append(phase_power)
            phase_voltage = rootmeansquare(data[vi])*config["Collector"]["CalibrationFactor_Voltage"]
            voltage.append(phase_voltage)
            phase_current = phase_power / phase_voltage
            current.append(phase_current)
            
            jsondata['l{}_current'.format(li+1)] = round(phase_current,3)
            jsondata['l{}_voltage'.format(li+1)] = round(phase_voltage,1)
            jsondata['l{}_power'.format(li+1)] = round(phase_power)

            #print("L{}: Current: {} A, Voltage: {} V, Power: {} W".format(li+1,round(current[li],3),round(voltage[li],1), round(power[li])))

        #print("Total: Current: {} A, Voltage: {} V, Power: {} W".format(round(sum(current),3),round(statistics.mean(voltage),1),round(sum(power))))
        
        jsondata['total_current'] = round(sum(current),3)
        jsondata['total_voltage'] = round(statistics.mean(voltage),1)
        jsondata['total_power'] = round(sum(power))
        
        with open(config["Collector"]["StateFile"], 'w+') as outfile:
            json.dump(jsondata, outfile)
    
        if(lastread != 0):
            now = time.perf_counter()
            readtime = now-lastread
            capacity = sum(power)*readtime/3600
            #counter += capacity/1000
            #print("Read time: {}, Capacity: {} Wh, Counter: {} KWh".format(round(readtime,3),round(capacity,5),round(counter,2)))
            lastread = now
    except Exception as e:
        print(e)
        logging.exception("Exception occurred, waiting 10 seconds before continueing")

        # Reset the SPI
        spi = spidev.SpiDev()
        spi.open(0,0)

        # Wait 10 seconds to avoid flooding the error log too much
        time.sleep(10)
