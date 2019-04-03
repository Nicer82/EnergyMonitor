import time
import math
import Adafruit_ADS1x15
import sqlite3
import datetime
import array
import json
import statistics

adc = Adafruit_ADS1x15.ADS1115()

start = time.time()
end = start + 0.1

adc.start(channel=0, gain=1, data_rate=860)

while (time.time() < end):
    value = adc.get_last_result()
    print(value)

adc.stop_adc()
