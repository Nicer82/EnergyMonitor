import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.ads1x15 import Mode
from adafruit_ads1x15.analog_in import AnalogIn

# Data collection setup
RATE = 860
SAMPLES = 1000

# Create the I2C bus with a fast frequency
i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)


chan0 = AnalogIn(ads, ADS.P0)
chan1 = AnalogIn(ads, ADS.P1)
#chan2 = AnalogIn(ads, ADS.P2)
#chan3 = AnalogIn(ads, ADS.P3)

# ADC Configuration
ads.mode = Mode.CONTINUOUS
ads.data_rate = RATE

data = [None]*SAMPLES

timebetweenreads = 1/RATE
print(timebetweenreads)
start = time.perf_counter()
nextRead = start

# Current = measured voltage - 2.5 / burden resistor ohms * CT turn ratio
# Read the same channel over and over
for i in range(SAMPLES):
    print("0;{}".format(chan0.voltage))

    nextRead += timebetweenreads
    sleep = nextRead-time.perf_counter()
    if sleep > 0:
      time.sleep(sleep)

    print("1;{}".format(chan1.voltage))

    nextRead += timebetweenreads
    sleep = nextRead-time.perf_counter()
    if sleep > 0:
      time.sleep(sleep)

end = time.monotonic()
total_time = end - start

print("Time of capture: {}s".format(total_time))
print("Sample rate requested={} actual={}".format(RATE, SAMPLES / total_time))
