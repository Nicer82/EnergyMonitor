import time
import statistics
import math
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.ads1x15 import Mode
from adafruit_ads1x15.analog_in import AnalogIn

# ADC settings
ADC_SAMPLESPERWAVE = 16
ADC_ACWAVESTOREAD = 125

# Mains properties
AC_FREQUENCY = 50

# CT properties
CT_TURNRATIO = 2000
CT_BURDENRESISTOR = 150

C_CALIBRATIONFACTOR = 1.022
V_CALIBRATIONFACTOR = 185.1

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
    end = round(start+1/AC_FREQUENCY*ADC_ACWAVESTOREAD,6)
    nextRead = start

    # Read the same channel over and over
    while(nextRead < end):
        sleep = nextRead-time.perf_counter()
        if sleep > 0:
            time.sleep(sleep)

        data.append(chan.voltage)
        
        nextRead = round(nextRead + 1/AC_FREQUENCY/ADC_SAMPLESPERWAVE,6)

    data = normalize(data)
    
    return data

def flowdirection(datac,datav):
    total = 0;
    
    for i in range(len(datac)):
        total += datac[i]*datav[i]
        
    return total/abs(total)
    

# Create the I2C bus with a fast frequency
i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)

chanc = AnalogIn(ads, ADS.P0)
chanv = AnalogIn(ads, ADS.P1)

# ADC Configuration
ads.mode = Mode.CONTINUOUS 
ads.data_rate = 860

while(True):
    ### Voltage measurement
    startv = round(time.perf_counter() + 0.1,6)
    datav = readadc(chanv, startv)
    
    voltage = rootmeansquare(datav) * V_CALIBRATIONFACTOR
    #print("Voltage: {} V, Reads: {}, VMin: {}, VMax: {}".format(voltage,len(datav),min(datav),max(datav)))
    
    ### Current measurement
    startc = startv
    while(startc < time.perf_counter() + 0.1): # add 100 ms to give time for python to get into readadc()
        startc = round(startc + 1/AC_FREQUENCY, 6) # add one wave at a time to perfectly match the sine wave with the current readout

    datac = readadc(chanc, startc)
    
    current = rootmeansquare(datac) / CT_BURDENRESISTOR * CT_TURNRATIO * flowdirection(datac,datav) * C_CALIBRATIONFACTOR
    #print("Current: {} A, Reads: {}, VMin: {}, VMax: {}".format(current,len(datac),min(datac),max(datac)))
    
    ### Power calculation
    power = current*voltage
    print("Current: {} A, Voltage: {} V, Power: {} W".format(round(current,3),round(voltage,1),round(power)))
    
    #print("Flow direction: {}".format(flowdirection(datac,datav)))
    #print("Value;Current;Voltage")
    #for i in range(len(datac)):
    #    print("{};{};{}".format(i,datac[i],datav[i]))
