import time
import statistics
import math
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.ads1x15 import Mode
from adafruit_ads1x15.analog_in import AnalogIn

# ADC settings
ADC_RATE = 800
ADC_ACWAVESTOREAD = 50
ADC_CALIBRATIONFACTOR = 1.032

# Mains properties
AC_FREQUENCY = 50

# CT properties
CT_TURNRATIO = 2000
CT_BURDENRESISTOR = 150

def rootmeansquare(values):
    # RMS = SQUARE_ROOT((values[0]² + values[1]² + ... + values[n]²) / LENGTH(values))
    sumsquares = 0.0
    avg = statistics.mean(values)

    for value in values:
        sumsquares = sumsquares + (value-avg)**2  # substract avg from value to correct the values and make sure we have the 0V line on the avg

    if len(values) == 0:
        rms = 0.0
    else:
        rms = math.sqrt(float(sumsquares)/len(values))

    return rms

def normalize(values):
    # Sometimes the ADC reports the same value twice, in that case, mean it out between the prev and next measurements
    for i in range(len(values)):
        if i > 1 and i < len(values)-1 and values[i] == values[i-1]:
            values[i-1] =  (values[i-2] + values[i-1]*2)/3
            values[i] = (values[i+1] + values[i]*2)/3
    
    # Remove the first and last half wave
    #for i in range(ADC_RATE/AC_FREQUENCY/2)
    
    return values

def readadc(chan,start):
    data = []
    end = start+(1/AC_FREQUENCY*ADC_ACWAVESTOREAD)
    nextRead = start
    time.sleep(start-time.perf_counter())

    # Read the same channel over and over
    while(nextRead < end):
        data.append(chan.voltage)
        
        nextRead += 1/ADC_RATE
        sleep = nextRead-time.perf_counter()
        if sleep > 0:
            time.sleep(sleep)

    data = normalize(data)
    
    return data

# Create the I2C bus with a fast frequency
i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)

chanc = AnalogIn(ads, ADS.P0)
chanv = AnalogIn(ads, ADS.P1)

# ADC Configuration
ads.mode = Mode.CONTINUOUS 
ads.data_rate = 860

if(True):
    ### Current measurement
    startc = time.perf_counter() + 0.1
    datac = readadc(chanc, startc)

    for i in range(len(datac)):
        print("{};{}".format(i,datac[i]))
    
    #current = rootmeansquare(datac) / CT_BURDENRESISTOR * CT_TURNRATIO * ADC_CALIBRATIONFACTOR
    #print("Current: {} A, VMin: {}, VMax: {}".format(current,min(datac),max(datac)))
    
    ### Voltage measurement
    startv = startc
    while(startv < time.perf_counter() + 0.1):
        startv += 1/AC_FREQUENCY
    
    datav = readadc(chanv, startv)
    
    for i in range(len(datav)):
        print("{};{}".format(i,datav[i]))
    
    #voltage = rootmeansquare(datav)
    #print("Voltage: {} V, VMin: {}, VMax: {}".format(voltage,min(datav),max(datav)))
    
    
