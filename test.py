import time
import statistics
import math
import emlib

# Settings
ADC_SAMPLESPERWAVE = 60 # If set to more then 400 with one channel, the code can't keep up, so that is about the max samples per wave
ADC_ACWAVESTOREAD = 10
AC_FREQUENCY = 50
CHANNELS = [0]

# Create the reader
reader = emlib.AdcReader()

while(True):
    ### Read the channels
    data = reader.readSineWave(CHANNELS, ADC_SAMPLESPERWAVE, ADC_ACWAVESTOREAD, AC_FREQUENCY)

    for i in range(len(data[0])):
        line = []
        for channeldataidx in range(len(data)):
            line.append(data[channeldataidx][i])
        print(';'.join(str(x) for x in line))
        
    ### Normalize the captured data
    for i in range(len(data)):
        #print("Channel {} before normalize: Reads: {}, Min: {}, Max: {}".format(i,len(data[i]),min(data[i]),max(data[i])))
        data[i] = emlib.normalize(data[i])
        #print("Channel {} after normalize: Reads: {}, Min: {}, Max: {}".format(i,len(data[i]),min(data[i]),max(data[i])))
        
    ### Calculate the power
    power = []
    voltage = []
    current = []
    
    for channel in [0,2,4]:
        powerdata = []                            
        li = round(channel/2)
        
        for reading in range(len(data[channel])):
            powerdata.append(data[channel][reading] * data[channel+1][reading])
        
        power.append(statistics.mean(powerdata)*CALIBRATIONFACTOR[li]);
        voltage.append(emlib.rootmeansquare(data[channel+1])*CALIBRATIONFACTOR_V[li])
        current.append(power[li]/voltage[li])
        print("L{}: Current: {} A, Voltage: {} V, Power: {} W".format(li+1,round(current[li],3),round(voltage[li],1), round(power[li])))
    
    print("Total: Current: {} A, Voltage: {} V, Power: {} W".format(round(sum(current),3),round(statistics.mean(voltage),1),round(sum(power))))
