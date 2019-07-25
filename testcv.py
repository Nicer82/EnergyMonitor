import time
import statistics
import math
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.ads1x15 import Mode
from adafruit_ads1x15.analog_in import AnalogIn

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
    for i in range(len(values)):
        if i > 1 and i < len(values)-1 and values[i] == values[i-1]:
            values[i-1] =  (values[i-2] + values[i-1]*2)/3
            values[i] = (values[i+1] + values[i]*2)/3
    
    return values
    
# ADC settings
ADC_RATE = 860
ADC_ACWAVESTOREAD = 50
ADC_CALIBRATIONFACTOR = 1.032

# Mains properties
AC_FREQUENCY = 50

# CT properties
CT_TURNRATIO = 2000
CT_BURDENRESISTOR = 150

# Create the I2C bus with a fast frequency
i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)

chanc = AnalogIn(ads, ADS.P0)
chanv = AnalogIn(ads, ADS.P1)

# ADC Configuration
ads.mode = Mode.CONTINUOUS 
ads.data_rate = ADC_RATE

if(True):
    ### Current measurement
    datac = []
    start = time.perf_counter()
    end = start+(1/AC_FREQUENCY*ADC_ACWAVESTOREAD)
    nextRead = start

    # Read the same channel over and over
    while(nextRead < end):
        datac.append(chanc.voltage)
        
        nextRead += 1/ADC_RATE
        sleep = nextRead-time.perf_counter()
        if sleep > 0:
            time.sleep(sleep)

    end = time.perf_counter()
    total_time = end - start

    datac = normalize(datac)

    for i in range(len(datac)):
        print(datac[i])
    
    current = rootmeansquare(datac) / CT_BURDENRESISTOR * CT_TURNRATIO * ADC_CALIBRATIONFACTOR
    #print("Time of capture: {}s".format(total_time))
    #print("Sample rate requested={} actual={}".format(ADC_RATE, len(datac) / total_time))
    print("Current: {} A, VMin: {}, VMax: {}".format(current,min(datac),max(datac)))
    
    ### Voltage measurement
    datav = []
    start = start+(1/AC_FREQUENCY*ADC_ACWAVESTOREAD)+1
    end = start+(1/AC_FREQUENCY*ADC_ACWAVESTOREAD)
    nextRead = start
    time.sleep(start-time.perf_counter())

    # Read the same channel over and over
    while(nextRead < end):
        datav.append(chanv.voltage)
        
        nextRead += 1/ADC_RATE
        sleep = nextRead-time.perf_counter()
        if sleep > 0:
            time.sleep(sleep)

    end = time.perf_counter()
    total_time = end - start

    datav = normalize(datav)
    
    for i in range(len(datav)):
        print(datav[i])
    
    voltage = rootmeansquare(datav)
    #print("Time of capture: {}s".format(total_time))
    #print("Sample rate requested={} actual={}".format(ADC_RATE, len(datav) / total_time))
    print("Voltage: {} W, VMin: {}, VMax: {}".format(voltage,min(datav),max(datav)))
