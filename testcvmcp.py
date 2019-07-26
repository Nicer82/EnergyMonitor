import time
import statistics
import math
import spidev

# Read settings
ADC_SAMPLESPERWAVE = 16
ADC_ACWAVESTOREAD = 50

# Mains properties
AC_FREQUENCY = 50

C_CALIBRATIONFACTOR = 1.022
V_CALIBRATIONFACTOR = 374.9 # with 10K Ohm burden resistor: 185.1

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

def readadc(chan,start):
    data = []
    
    # Validate if channel is 0-7
    if adcnum > 7 or adcnum < 0:
        return data
    
    end = round(start+1/AC_FREQUENCY*ADC_ACWAVESTOREAD,6)
    nextRead = start

    # Read the same channel over and over
    while(nextRead < end):
        sleep = nextRead-time.perf_counter()
        if sleep > 0:
            time.sleep(sleep)

        r = spi.xfer2([1, 8 + chan << 4, 0])
        data.append(((r[1] & 3) << 8) + r[2])
        
        nextRead = round(nextRead + 1/AC_FREQUENCY/ADC_SAMPLESPERWAVE,6)

    print("Before normalize: Reads: {}, Min: {}, Max: {}".format(len(data),min(data),max(data)))

    data = normalize(data)
    
    print("After normalize: Reads: {}, VMin: {}, VMax: {}".format(len(data),min(data),max(data)))
    
    return data

def flowdirection(datac,datav):
    total = 0;
    
    for i in range(len(datac)):
        total += datac[i]*datav[i]
        
    return total/abs(total)
    

# Create the SPI
spi = spidev.SpiDev()
spi.open(0,0)

while(True):
    ### Voltage measurement
    startv = round(time.perf_counter() + 0.1,6)
    datav = readadc(1, startv)
    
    voltage = rootmeansquare(datav) * V_CALIBRATIONFACTOR
    
    ### Current measurement
    startc = startv
    while(startc < time.perf_counter() + 0.1): # add 100 ms to give time for python to get into readadc()
        startc = round(startc + 1/AC_FREQUENCY, 6) # add one wave at a time to perfectly match the sine wave with the current readout

    datac = readadc(0, startc)
    
    current = rootmeansquare(datac) * flowdirection(datac,datav) * C_CALIBRATIONFACTOR
    
    ### Power calculation
    power = current*voltage
    print("Current: {} A, Voltage: {} V, Power: {} W".format(round(current,3),round(voltage,1),round(power)))
    
    #print("Value;Current;Voltage")
    #for i in range(len(datac)):
    #    print("{};{};{}".format(i,datac[i],datav[i]))
