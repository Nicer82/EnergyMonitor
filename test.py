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
SAMPLES = 1000

# Create the I2C bus with a fast frequency
i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)

chan0 = AnalogIn(ads, ADS.P0)

# ADC Configuration
ads.mode = Mode.CONTINUOUS 
ads.data_rate = RATE

data0 = [None]*SAMPLES

timebetweenreads = 1/RATE
while(True):
    start = time.perf_counter()
    nextRead = start

    # Current = measured voltage - 2.5 / burden resistor ohms * CT turn ratio
    # Read the same channel over and over
    for i in range(SAMPLES):
        data0[i] = chan0.voltage
        #print(data0[i])

        nextRead += timebetweenreads
        sleep = nextRead-time.perf_counter()
        if sleep > 0:
          time.sleep(sleep)

    end = time.perf_counter()
    total_time = end - start
    power = rootmeansquare(data0)/100*2000*230
    power = int(power/0.35095)*0.35095
    #print("Time of capture: {}s".format(total_time))
    #print("Sample rate requested={} actual={}".format(RATE, SAMPLES / total_time))
    print("Power: {} Watt".format(power))
