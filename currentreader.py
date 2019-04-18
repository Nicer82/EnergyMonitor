#!/usr/bin/python3
# -------------------------------------------------------------------------
# Program: Class that handles reading out AC current sensors over the ADS1115
#
# Copyright (C) 2019 Bjorn Douchy
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License at https://www.gnu.org/licenses
#    for more details.
# -------------------------------------------------------------------------import time
import math
import Adafruit_ADS1x15
import array
import statistics
import time

class CurrentReader():
    def __init__(self,voltage=230,frequency=50):
        self._voltage = voltage
        self._frequency = frequency
        self._movingAverageWaves = 3 # the number of sine waves to take into account to calculate the moving average. Should be a whole number.

        self._adc = Adafruit_ADS1x15.ADS1115()
        self._adcReadTime = 0.5 # how long do we read out the sine wave in seconds to get a reliable and stable readout
        self._adcGain = 1 # gain factor, for reading lower currents
        self._adcDataRate = 860 # samples per second

        self._movingAverageValues = round(self._adcDataRate / self._frequency * self._movingAverageWaves) # the number of values to take into account for moving average calculation.
    def _rootmeansquare(self, values):
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
    def _rootmovingaveragesquare(self, values):
        sumsquares = 0.0
        
        if len(values) > self._movingAverageValues:
            useablevalues = values[int(self._movingAverageValues/2):int(len(values)-self._movingAverageValues/2)+1]
            index = 0

            for value in useablevalues:
                mavalues = values[index:index+self._movingAverageValues]
                sumsquares = sumsquares + (value-statistics.mean(maValues))**2
                index = index + 1
        
            rmas = math.sqrt(float(sumsquares)/numsquares)
        else:
            rmas = 0.0
            
        return rmas
    
    def readChannel(self, chan, ampFactor,ampExponent=1,ampMinimum=0,cycle=0):
        readValues = []
        
        self._lastStart = time.time()
        self._lastEnd = self._lastStart + self._adcReadTime
        self._adc.start_adc(channel=chan, gain=self._adcGain, data_rate=self._adcDataRate)
        interval = 1/self._adcDataRate
        nextRead = self._lastStart

        while (time.time() < self._lastEnd):
            val = self._adc.get_last_result()
            
            nextRead = nextRead+interval
            sleep = nextRead-time.time()
            
            if sleep > 0:
                time.sleep(sleep)
            
            #print(val)
            
            readValues.append(val)
            
        self._adc.stop_adc()
        self._lastAmps = (self._rootmovingaveragesquare(readValues)*ampFactor)**ampExponent
        
        # measurements might only be accurate from a certain value, so lower values are considered 0
        if(self._lastAmps < ampMinimum):
            self._lastAmps = 0
            
        self._lastWatts = self._lastAmps*self._voltage
        
        return
    
    def lastCurrent(self):
        return self._lastAmps

    def lastPower(self):
        return self._lastWatts

    def lastStart(self):
        return self._lastStart

    def lastEnd(self):
        return self._lastEnd
