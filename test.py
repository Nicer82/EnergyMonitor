import time
import statistics
import math
import emlib
import spidev

# Settings
ADC_SAMPLESPERWAVE = 10 # If set to more then 400 with one channel, the code can't keep up, so that is about the max samples per wave
ADC_ACWAVESTOREAD = 50
AC_FREQUENCY = 50
CHANNELS = [0]

# Create the reader
#reader = emlib.AdcReader()

spi = spidev.SpiDev()
spi.open(0,0)
channel=0
response = spi.xfer2([6+((4&channel)>>2),(3&channel)<<6,0], 2000000)
print(response)

while(False):
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
