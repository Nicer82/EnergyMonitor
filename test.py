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

# Data collection setup
RATE = 860
MEASURETIME = 0.2
PRECISION = 0.001516 # 2x the stdev of a large testgroup when measured with 0v at input

# Create the I2C bus with a fast frequency
i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)

chan0 = AnalogIn(ads, ADS.P0)

# ADC Configuration
ads.mode = Mode.CONTINUOUS 
ads.data_rate = RATE

data = []

timebetweenreads = 1/RATE
#while(True):
start = time.perf_counter()
last = start
#nextRead = start

# Current = measured voltage - 2.5 / burden resistor ohms * CT turn ratio
# Read the same channel over and over
while(last < start+MEASURETIME):
    value = chan0.voltage
    while(value == data[data.count()-1]):
       value = chan0.voltage
    
    data.append(value)
    
    last = time.perf_counter()
    
    print("{}\t{}".format(last,value))

    #nextRead += timebetweenreads
    #sleep = nextRead-time.perf_counter()
    #if sleep > 0:
    #  time.sleep(sleep)

end = time.perf_counter()
total_time = end - start
power = rootmeansquare(data)/100*2000*230
print("Time of capture: {}s".format(total_time))
print("Sample rate requested={} actual={}".format(RATE, data.count() / total_time))
print("Power: {} Watt".format(power))
