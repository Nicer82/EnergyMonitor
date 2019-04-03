import time
import math
import Adafruit_ADS1x15
import sqlite3
import datetime
import array
import json
import statistics

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

adc = Adafruit_ADS1x15.ADS1115()

ampFactor = 0.002667
ampMinimum = 0.015
volt = 230

while(True):
    adc.start_adc(channel=0, gain=1, data_rate=860)
    start = time.time()
    end = start + 0.25
    values = []

    while (time.time() < end):
        value = adc.get_last_result()
        values.append(value)
        #print(value)

    adc.stop_adc()

    amps = rootmeansquare(values)*ampFactor
    
    # measurements are only accurate starting around 15 mA, so lower values are considered 0
    
    if(amps < ampMinimum):
        amps = 0
        
    #print("Mean : {0}".format(statistics.mean(values)))
    #print("Min  : {0}".format(min(values)))
    #print("Max  : {0}".format(max(values)))
    #print("Stdev: {0}".format(statistics.stdev(values)))
    #print("Rms  : {0}".format(rootmeansquare(values)))
    print("Current: {0}".format(amps))
    print("Power: {0}".format(amps*volt))
