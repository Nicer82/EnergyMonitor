import time
import statistics
import math
import spidev

# Read settings
ADC_SAMPLESPERWAVE = 60 # If set to more then 400 with one channel, the code can't keep up, so that is about the max samples per wave
ADC_ACWAVESTOREAD = 50

# Mains properties
AC_FREQUENCY = 50

counter = 8632.74
lastread = time.perf_counter()
CHANNELS = [0,1,2,3,4,5]
CALIBRATIONFACTOR = [0.004047,0.004047,0.004047]
CALIBRATIONFACTOR_V = [0.2475,0.2475,0.2475]
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

def readadc(channels):
    data = []
    
    for i in channels:
        data.append([])
        
    start = time.perf_counter()
    nextRead = start

    for i in range(ADC_SAMPLESPERWAVE*ADC_ACWAVESTOREAD):
        nextRead += 1/(ADC_SAMPLESPERWAVE*AC_FREQUENCY)

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

def flowdirection(datac,datav):
    total = 0
    
    for i in range(len(datac)):
        total += datac[i]*datav[i]
    
    if total != 0:
        return total/abs(total)
    
    return 0

# Create the SPI
spi = spidev.SpiDev()
spi.open(0,0)


while(True):
    ### Read the channels
    data = readadc(CHANNELS)

    ### Normalize the captured data
    for i in range(len(data)):
        #print("Channel {} before normalize: Reads: {}, Min: {}, Max: {}".format(i,len(data[i]),min(data[i]),max(data[i])))
        data[i] = normalize(data[i])
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
        voltage.append(rootmeansquare(data[channel+1])*CALIBRATIONFACTOR_V[li])
        current.append(power[li]/voltage[li])
        
        #print("L{}: Current: {} A, Voltage: {} V, Power: {} W".format(li+1,round(current[li],3),round(voltage[li],1), round(power[li])))
    
    #print("Total: Current: {} A, Voltage: {} V, Power: {} W".format(round(sum(current),3),round(statistics.mean(voltage),1),round(sum(power))))
    
    if(lastread != 0):
        now = time.perf_counter()
        readtime = now-lastread
        capacity = sum(power)*readtime/3600
        counter += capacity/1000
        print("Read time: {}, Capacity: {} Wh, Counter: {} KWh".format(round(readtime,3),round(capacity,5),round(counter,2)))
        lastread = now
spi.close()
