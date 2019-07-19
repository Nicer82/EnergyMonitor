import math
import Adafruit_ADS1x15
import array
import statistics
import time

_adc = Adafruit_ADS1x15.ADS1115()
_adcChannel = 0
_adcReadTime = 0.5 # how long do we read out the sine wave in seconds to get a reliable and stable readout
_adcGain = 1 # gain factor, for reading lower currents
_adcDataRate = 860 # samples per second

_adc.start_adc(channel=_adcChannel, gain=_adcGain, data_rate=_adcDataRate)

_start = time.time()

while (time.time() < _start + 1):
  val = _adc.get_last_result()

  print(val)

self._adc.stop_adc()
