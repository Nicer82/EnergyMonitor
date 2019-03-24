#!/usr/bin/python3
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
    ssq = 0.0
    sum = 0.0
    avg = statistics.mean(values)
    
    for value in values:
        newValue = value - avg
        ssq = ssq + newValue * newValue
        sum = sum + newValue

    # Figure the RMS, which is the square root of the average of the
    # sum of squares figured above
    if len(values) == 0:
        rms = 0.0
    else:
        rms = math.sqrt(float(ssq)/len(values))
    
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
          #print('{0};{1};{2}'.format(value,self._lastStart,chan))

      # Stop continuous conversion.
      self._adc.stop_adc()

      return values

  # Read and compute the amperage on the specified channel
  def read(self, chan=0):
      self._chan = chan

      try:
          values = self.readChannel(chan)
      except ValueError as e:
          print("ADC configuration error: ", e)
          exit()
      except Exception as e:
          print("Unexpected ADC error: ", e)
          exit()

      avgmax = self.rootmeansquare(values)
      amps = (avgmax - self._config["Reader"]["Substractor"]) * self._config["Reader"]["Factor"]
      
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
