#!/usr/bin/python
import time
import math
import Adafruit_ADS1x15
import sqlite3
import datetime
import array
import json

# Calculate the average value
def averagemax( values ):
    maxvalues = []
    prev = 0.0
    prevmax = -1.0
    startcollection = False
    
    for value in values:
        # Has the AC sinus passed the zero line?
        if(value*prev < 0.0):
            if(startcollection):
                maxvalues.append(prevmax)
                prevmax = 0.0
            else:
                startcollection = True
        
        # Only set prevmax when zero line is passed for the first time
        if(startcollection and abs(value) > prevmax):
            prevmax = abs(value)
        
        prev = value
   
    avgmax = average(maxvalues)
    
    return avgmax

# Calculate the average value
def average( values ):
    sum = 0
    for value in values:
        sum = sum + value
    avg = sum/len(values)    
    return avg

# Read an ADC channel with the specified gain at max rate for 1 second
def readChannel( adc, chan, g ):
    values = []
    adc.start_adc(chan, gain=g, data_rate=860)
    # Sample for one second
    start = time.time()
    while (time.time() - start) <= 1.0:
        # Read the last ADC conversion value and print it out.
        value = float(adc.get_last_result())
        values.append(value)
        #print('{0};{1};{2}'.format(time.time(),chan,value))

    # Stop continuous conversion.
    adc.stop_adc()

    return values

# Read and compute the amperage on the specified channel
def readAmps( adc, chan, config ):
    print("Sampling", chan)
    GAIN = config["Sampler"]["gain"]
    SUBSTRACTOR = config["Sampler"]["substractor"]
    FACTOR = config["Sampler"]["factor"]

    # The inductive sensor returns an AC voltage. Sample at the
    # maximum rate for 1 second.  Then calculate the RMS of
    # the sampled readings
    print("Sampling started.")

    try:
        values = readChannel( adc, chan, GAIN)
        print("Sampling stopped")
    except ValueError as e:
        print("ADC configuration error: ", e)
        exit()
    except Exception as e:
        print("Unexpected ADC error: ", e)
        exit()
        
    avgmax = averagemax(values)
    print("avgmax:",avgmax)
    
    # Polynomial regression to estimate amps
    # Constants stored in config file.
    temp = (avgmax - SUBSTRACTOR) * FACTOR
    #print("substractor",SUBSTRACTOR)
    #print("factor", FACTOR)

    #Round to 3 decimal places
    amps = round(temp, 3)
    
    print('Average Reading in Amps: {0}'.format(amps))
    print('Average Reading in Watt: {0}'.format(amps * config["Voltage"]))
    
    return amps
