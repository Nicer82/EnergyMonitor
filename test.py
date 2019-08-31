import time
import statistics
import math
import emlib
import spidev

# Settings
ADC_SAMPLESPERWAVE = 16 # If set to more then 400 with one channel, the code can't keep up, so that is about the max samples per wave
ADC_ACWAVESTOREAD = 50
AC_FREQUENCY = 50
CHANNELS = [0,1,2,3,4,5,6,7]

# Create the reader
reader = emlib.AdcReader()

while(True):
    print(time.perf_counter())
    
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
