import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.ads1x15 import Mode
from adafruit_ads1x15.analog_in import AnalogIn

# Data collection setup
RATE = 250
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

start = time.monotonic()

start = time.perf_counter()
time.sleep(1)
end = time.perf_counter()
print(end-start)

# Current = measured voltage - 2.5 / burden resistor ohms * CT turn ratio
# Read the same channel over and over
#for i in range(SAMPLES):
#    print("0;{}".format(chan0.voltage))
#    print("1;{}".format(chan1.voltage))
#    print(chan0.voltage) 
#    print(chan1.voltage)
#    print(chan2.voltage)
#    print(chan3.voltage)

end = time.monotonic()
total_time = end - start

print("Time of capture: {}s".format(total_time))
print("Sample rate requested={} actual={}".format(RATE, SAMPLES / total_time))
