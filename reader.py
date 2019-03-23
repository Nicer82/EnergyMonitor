#!/usr/bin/python
import time
import math
import Adafruit_ADS1x15
import sqlite3
import datetime
import array
import json

class Reader():
  def __init__(self,config,chan=0,adc=Adafruit_ADS1x15.ADS1115()):
    self._adc = adc
    self._chan = chan
    self._config = config
    
  # Calculate the average value
  def averagemax(self,values):
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

      avgmax = self._average(maxvalues)

      return avgmax

  # Calculate the average value
  def average(self,values):
      sum = 0
      for value in values:
          sum = sum + value
      avg = sum/len(values)    
      return avg

  # Read an ADC channel with the specified gain at max rate for 1/4 second
  def readChannel(self):
      values = []
      
      self._adc.start_adc(self._chan, gain=self._config["Sampler"]["gain"], data_rate=860)
      
      # Sample for one second
      start = time.time()
      while (time.time() - start) <= 0.25:
          # Read the last ADC conversion value and print it out.
          value = float(self._adc.get_last_result())
          values.append(value)
          #print('{0};{1};{2}'.format(time.time(),chan,value))

      # Stop continuous conversion.
      self._adc.stop_adc()

      return values

  # Read and compute the amperage on the specified channel
  def read(self):
      SUBSTRACTOR = self._config["Sampler"]["substractor"]
      FACTOR = self._config["Sampler"]["factor"]

      try:
          values = self._readChannel()
      except ValueError as e:
          print("ADC configuration error: ", e)
          exit()
      except Exception as e:
          print("Unexpected ADC error: ", e)
          exit()

      avgmax = self._averagemax(values)
      
      # Polynomial regression to estimate amps
      # Constants stored in config file.
      amps = (avgmax - SUBSTRACTOR) * FACTOR
      
      #Round to 3 decimal places and suppress values below zero
      amps = round(amps, 3)
      if(amps < 0.0):
          amps = 0.0
      
      self._lastCurrent = amps
      self._lastPower = amps * self._config["Voltage"]

      return
    
  def getLastCurrent(self):
    return self._lastCurrent
  
  def getLastPower(self):
    return self._lastPower
