#!/usr/bin/python3
# -------------------------------------------------------------------------
# Program: Class that handles reading out current sensors over the ADS1115
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
# -------------------------------------------------------------------------
import time
import math
import Adafruit_ADS1x15
import sqlite3
import datetime
import array
import json
import statistics

class Reader():
  def __init__(self,config):
    self._adc = Adafruit_ADS1x15.ADS1115()
    self._config = config
    
  def rootmeansquare(self,values):
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

  # Read an ADC channel with the specified gain at max rate for 1/4 second
  def readChannel(self, chan):
      values = []
      
      self._adc.start_adc(chan, gain=self._config["Reader"]["Gain"], data_rate=self._config["Reader"]["DataRate"])
      
      # Sample for 1/4 second
      self._lastStart = time.time()
      while (time.time() - self._lastStart) <= self._config["Reader"]["ReadTime"]:
          # Read the last ADC conversion value and print it out.
          value = float(self._adc.get_last_result())
          values.append(value)
          print('{0};{1};{2}'.format(value,self._lastStart,chan))

      # Stop continuous conversion.
      self._adc.stop_adc()

      return values

  # Read and compute the amperage on the specified channel
  def read(self, chan=0):
      self._chan = chan

      values = self.readChannel(chan)
      rms = self.rootmeansquare(values)
      amps = (rms - self._config["Reader"]["Substractor"]) * self._config["Reader"]["AmpFactor"]
      
      # Suppress values below zero
      if(amps < 0.0):
          amps = 0.0
      
      self._lastCurrent = amps
      self._lastPower = amps * self._config["Reader"]["Voltage"]

      return
    
  def getLastCurrent(self):
    return self._lastCurrent
  
  def getLastPower(self):
    return self._lastPower
  
  def getLastStart(self):
    return self._lastStart

# Read configuration
with open('/home/pi/EnergyMonitor/config.json') as json_data:
    config = json.load(json_data)

r = Reader(config)
r.read(0)
