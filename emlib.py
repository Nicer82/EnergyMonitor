import time
import statistics
import math
import spidev
import subprocess
import operator

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
                else:
                    response = self.spi.xfer2([6+((4&channel)>>2),(3&channel)<<6,0], 2000000)

                data[ci].append(((response[1] & 15) << 8) + response[2])

            # Set the next read time for the next iteration
            nextRead += sampleReadTime

        return data
    
    
class VoltageService:
    def __init__(self, url, samplesperwave, wavestoread, calibrationfactor):
        self.url = url
        self.samplesperwave = samplesperwave
        self.wavestoread = wavestoread
        self.calibrationfactor = calibrationfactor

        #TODO Periodically fetch wire voltages from url in separate thread. Hardcoded for now.
        self.voltage={}
        self.voltage["brown"] = 240
        self.voltage["black"] = 240
        self.voltage["gray"] = 240

    def calcPeakSampleIdx(self, values):
        indexes = []
        
        for i in range(int(len(values)/self.samplesperwave)):
            wave = values[i*self.samplesperwave:(i+1)*self.samplesperwave]
            maxidx, maxvalue = max(enumerate(wave), key=operator.itemgetter(1))
            indexes.append(maxidx)

        return round(statistics.mean(indexes)) 

    def wireVoltageData(self, wirecolor, currentData):
        #TODO
        return self.simulateSineWave(peaksampleidx=self.calcPeakSampleIdx(currentData),peaksamplevalue = round(self.voltage[wirecolor]/self.calibrationfactor*math.sqrt(2)))
        
    def simulateSineWave(self, peaksampleidx, peaksamplevalue):
        data = []
        
        # Loop through the total number of samples to take
        for si in range(self.samplesperwave*self.wavestoread):
            data.append(round(math.sin((si+self.samplesperwave/4-peaksampleidx)/self.samplesperwave*2*math.pi)*peaksamplevalue))
        
        return data
