import time
import statistics
import math
import spidev
import subprocess
import operator
import json
import threading

def run_process(cmd):
    return subprocess.check_output(cmd, shell=True)

def rootmeansquare(values):
    # RMS = SQUARE_ROOT((values[0]² + values[1]² + ... + values[n]²) / LENGTH(values))
    sumsquares = 0.0

    for value in values:
        sumsquares = sumsquares + (value)**2 

    if len(values) == 0:
        rms = 0.0
    else:
        rms = math.sqrt(float(sumsquares)/len(values))

    return rms

def normalize(values):
    avg = round(statistics.mean(values))

    # Substract the mean of every value to set the mean to 0
    for i in range(len(values)):
        values[i] -= avg
        
    return values

def calcPeakSampleIdx(values, samplesperwave):
    indexes = []
    
    for i in range(int(len(values)/samplesperwave)):
        wave = values[i*samplesperwave:(i+1)*samplesperwave]
        maxidx, maxvalue = max(enumerate(wave), key=operator.itemgetter(1))
        indexes.append(maxidx)

    return round(statistics.mean(indexes))

class AdcReader():
    def __init__(self):
        self.spi = spidev.SpiDev()
        self.spi.open(0,0)
        
    def readSineWave(self, channels, samplesperwave, wavestoread, frequency):
        # Initialize the data object
        data = []
        for channel in channels:
            data.append([])
        
        start = time.perf_counter()
        sampleReadTime = 1/(samplesperwave*frequency)
        nextRead = start + sampleReadTime
        lastChannel = channels[len(channels)-1]
        channelIndexes = range(len(channels))
        countNoDelay = 0
        # Loop through the total number of samples to take
        for si in range(samplesperwave*wavestoread):
            # Read all the requested channels
            for ci in channelIndexes:
                channel = channels[ci]
                # Add a delay on the last channel to match timings. 
                # This is way more accurate than time.sleep() because it works up to the microsecond.
                if(channel == lastChannel):
                    delay = int((nextRead-time.perf_counter())*1000000)
                    if(delay > 0): 
                        response = self.spi.xfer2([6+((4&channel)>>2),(3&channel)<<6,0], 2000000, delay) 
                    else:
                        response = self.spi.xfer2([6+((4&channel)>>2),(3&channel)<<6,0], 2000000)
                        countNoDelay += 1
                else:
                    response = self.spi.xfer2([6+((4&channel)>>2),(3&channel)<<6,0], 2000000)

                data[ci].append(((response[1] & 15) << 8) + response[2])
        
            # Set the next read time for the next iteration
            nextRead += sampleReadTime
            
            if(countNoDelay > 0):
                print('WARNING: Sampling was too late in {}/{} samples ({}%). Try reducing samplesperwave.'.format(countNoDelay,samplesperwave*wavestoread,countNoDelay/(samplesperwave*wavestoread)*100))
            
        return data
    
class VoltageService:
    def __init__(self, url, samplesperwave, wavestoread, calibrationfactor):
        self._url = url
        self._samplesperwave = samplesperwave
        self._wavestoread = wavestoread
        self._calibrationfactor = calibrationfactor
        self.voltage = {}
        self.refreshVoltages(False)

        # Start a thread to periodically refresh the voltages
        self.refreshVoltagesThread = threading.Thread(target=self.refreshVoltages)
        self.refreshVoltagesThread.start()

    def refreshVoltages(self, nonstop=True):
        attempt = True
        while(attempt):
            try:
                time.sleep(1)
                res = run_process('curl -s -m 5 -H "Content-Type: application/json" {}'.format(self._url))
                data = json.loads(res)

                # TODO available colors should be fetched from the json
                self.voltage["brown"] = data["brown"]["voltage"]
                self.voltage["black"] = data["black"]["voltage"]
                self.voltage["gray"] = data["gray"]["voltage"]

                # if we reach this point, fetching succeeded, so we can stop attempting if not running nonstop.
                if(not nonstop):
                    attempt = False 
            except Exception as e:
                # In case of an error, just try again.
                continue

    def calcPeakSampleIdx(self, values):
        indexes = []
        
        for i in range(int(len(values)/self._samplesperwave)):
            wave = values[i*self._samplesperwave:(i+1)*self._samplesperwave]
            maxidx, maxvalue = max(enumerate(wave), key=operator.itemgetter(1))
            indexes.append(maxidx)
        
        return round(statistics.mean(indexes)) 

    def wireVoltageData(self, wirecolor, currentData):
        #peakCurrentValue = rootmeansquare(currentData)/(1/math.sqrt(2))
        #peakVoltageValue = self.voltage[wirecolor]/self._calibrationfactor*math.sqrt(2)
        #ret = []
        #for value in currentData:
        #    ret.append(round(value/peakCurrentValue*peakVoltageValue))
        #return ret;
        return self.simulateSineWave(peaksampleidx=self.calcPeakSampleIdx(currentData),peaksamplevalue = round(self.voltage[wirecolor]/self._calibrationfactor*math.sqrt(2)))
        
    def simulateSineWave(self, peaksampleidx, peaksamplevalue):
        ret = []
        
        # Loop through the total number of samples to take
        for si in range(self._samplesperwave*self._wavestoread):
            ret.append(round(math.sin((si+self._samplesperwave/4-peaksampleidx)/self._samplesperwave*2*math.pi)*peaksamplevalue))
        
        return ret
