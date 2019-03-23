#!/usr/bin/python

import time
import math
import Adafruit_ADS1x15
import sqlite3
import datetime
import array
import json

# Calculate RMS excluding noisey values more than 3x std dev
def rootmeansquare( values, avg, stddev, bias):
    ssq = 0.0
    sum = 0.0
    n = 0

    for value in values:
        newValue = value + bias
        # Skip values more that 3x stddev
        if abs(value) < avg + 3*stddev:
            ssq = ssq + newValue * newValue
            sum = sum + newValue
            n = n + 1

    # Figure the RMS, which is the square root of the average of the
    # sum of squares figured above
    if n == 0:
        rms = 0.00
    else:
        rms = math.sqrt(float(ssq)/n)
    print('RMS: {0}'.format(rms))
    return rms

# Calculate the average value
def average( values ):
    sum = 0
    for value in values:
        sum = sum + value
    avg = sum/len(values)    
    return avg

# Calculate sum of squares
def sumsquares( values ):
    ssq = 0
    for value in values:
        ssq = ssq + value*value
    return ssq

# Read an ADC channel with the specified gain at max rate for 1 second
def readChannel( adc, chan, g ):
    values = []
    adc.start_adc(chan, gain=g, data_rate=860)
    # Sample for one second
    start = time.time()
    while (time.time() - start) <= 0.1:
        # Read the last ADC conversion value and print it out.
        value = float(adc.get_last_result())
        values.append(value)
        #print('Channel {0}: {1}'.format(chan,value))

    # Stop continuous conversion.
    adc.stop_adc()

    return values

# Read and compute the amperage on the specified channel
def readAmps( adc, chan, config ):
    print("Sampling", chan)
    GAIN = config["Sampler"]["gain"]
    SUBSTRACTOR = config["Sampler"]["substractor"]
    FACTOR = config["Sampler"]["factor"]

    n = 0
    sum = 0.0
    ssq = 0
    rms = 0
    max = 0
    min = 0
    amps = 0
    values = []

    # The inductive sensor returns an AC voltage. Sample at the
    # maximum rate for 1 second.  Then calculate the RMS of
    # the sampled readings
    print("Sampling started.")

    try:
        values = readChannel( adc, chan, GAIN)
        n = len(values)
        print("Sampling stopped")
    except ValueError as e:
        print("ADC configuration error: ", e)
        exit()
    except Exception as e:
        print("Unexpected ADC error: ", e)
        exit()
        
    # Calculate basic stats on the raw data
    avg = average(values)
    ssq = sumsquares( values )
    bias = -avg
    #print("ssq ", ssq)
    #print("avg", avg)
    #print("bias", bias)

    variance = float(ssq)/n - avg*avg
    #print("variance", variance)
    stddev = math.sqrt(variance)
    #print("stddev", stddev)

    # Calculate the RMS
    rms = rootmeansquare( values, avg, stddev, bias)

    # Polynomial regression to estimate amps
    # Constants stored in config file.
    temp = (rms - SUBSTRACTOR) * FACTOR
    print("substractor",SUBSTRACTOR)
    print("factor", FACTOR)

    #Round to 2 decimal places
    amps = round(temp, 3)
    if amps < 0:
        amps = 0.00
    print('Average Reading in Amps: {0}'.format(amps))
    print('Average Reading in Watt: {0}'.format(amps*240))
    
    return amps
