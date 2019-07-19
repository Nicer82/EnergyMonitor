import math
import Adafruit_ADS1x15
import array
import statistics
import time

_adc = Adafruit_ADS1x15.ADS1115()
_adcChannel = 0
_adcReadTime = 1 # how long do we read out the sine wave in seconds to get a reliable and stable readout
_adcGain = 1 # gain factor, for reading lower currents
_adcDataRate = 860 # samples per second

readValues = []
        
_lastStart = time.time()
_lastEnd = _lastStart + _adcReadTime
_adc.start_adc(channel=_adcChannel, gain=_adcGain, data_rate=_adcDataRate)
interval = 1/_adcDataRate
nextRead = _lastStart

while (time.time() < _lastEnd):
    val = _adc.get_last_result()

    nextRead = nextRead+interval
    sleep = nextRead-time.time()

    if sleep > 0:
        time.sleep(sleep)

    print(val)

_adc.stop_adc()
