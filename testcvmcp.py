import time
import statistics
import math
import spidev

# Read settings
ADC_SAMPLESPERWAVE = 60 # If set to more then 400 with one channel, the code can't keep up, so that is about the max samples per wave
ADC_ACWAVESTOREAD = 50

# Mains properties
AC_FREQUENCY = 50

C_CALIBRATIONFACTOR = 1.022
V_CALIBRATIONFACTOR = 0.239



def rootmeansquare(values):
    # RMS = SQUARE_ROOT((values[0]² + values[1]² + ... + values[n]²) / LENGTH(values))
    sumsquares = 0.0
    avg = statistics.mean(values)

    for value in values:
        sumsquares = sumsquares + (value)**2  # substract avg from value to correct the values and make sure we have the 0V line on the avg

    if len(values) == 0:
        rms = 0.0
    else:
        rms = math.sqrt(float(sumsquares)/len(values))

    return rms

def normalize(values):
    avg = statistics.mean(values)

    # Substract the mean of every value to set the mean to 0
    for i in range(len(values)):
        values[i] -= avg
        
    # Sometimes the ADC reports the same value twice, in that case, mean it out between the prev and next measurements
    #for i in range(len(values)):
    #    if i > 1 and i < len(values)-1 and values[i] == values[i-1]:
    #        values[i-1] =  (values[i-2] + values[i-1]*2)/3
    #        values[i] = (values[i+1] + values[i]*2)/3
    
    # Remove the first and last half wave
    for i in range(int(ADC_SAMPLESPERWAVE/2)):
        values.pop(0)
        values.pop(len(values)-1)
    
    return values

def readadc(channels):
    
    data = [[],[]]
    start = time.perf_counter()
    nextRead = start

    for i in range(ADC_SAMPLESPERWAVE*ADC_ACWAVESTOREAD):
        nextRead += 1/(ADC_SAMPLESPERWAVE*AC_FREQUENCY)
        datasample = []

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

    #for datasample in data:
    #    print("{};{}".format(datasample[0],datasample[1]))

    #print("Reads: {}, Performance: {} sps, Requested time: {} ms, Actual time: {} ms".format(len(data),len(data)/(end-start),1000/AC_FREQUENCY*ADC_ACWAVESTOREAD,(end-start)*1000))
    
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

channels = [0,1]

if(True):
    data = readadc(channels)
    datac = data[0]
    datav = data[1]
    
    print("Current data: Before normalize: Reads: {}, Min: {}, Max: {}".format(len(datac),min(datac),max(datac)))
    print("Voltage data: Before normalize: Reads: {}, Min: {}, Max: {}".format(len(datav),min(datav),max(datav)))

    datac = normalize(datac)
    datav = normalize(datav)
    
    print("Current data: After normalize: Reads: {}, Min: {}, Max: {}".format(len(datac),min(datac),max(datac)))
    print("Voltage data: After normalize: Reads: {}, Min: {}, Max: {}".format(len(datav),min(datav),max(datav)))

    voltage = rootmeansquare(datav) * V_CALIBRATIONFACTOR
    current = rootmeansquare(datac) * flowdirection(datac,datav) * C_CALIBRATIONFACTOR
    
    ### Power calculation
    power = current*voltage
    print("Current: {} A, Voltage: {} V, Power: {} W".format(round(current,3),round(voltage,1),round(power)))

spi.close()
