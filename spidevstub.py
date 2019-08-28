# Stub for SpiDev on RPI returning random results
import time
import math

class SpiDev:
    peakvalue = 3500 # This should result in approximately 17A and 252V
    samplesperwave = 60
    frequency = 50
    readtime = 1/(samplesperwave*frequency)
    
    def open(self, bus, device):
        return
    def sleep(self, seconds):
        start = time.perf_counter()
        end = start+seconds
        while(time.perf_counter()<end):
            continue

        return
    def xfer2(self, values, speed_hz = 0, delay_usec = 0, bits_per_word = 8):
        start = time.perf_counter()
        value = round(math.sin(round(start/SpiDev.readtime)/SpiDev.samplesperwave*2*math.pi)*(SpiDev.peakvalue-2048))+2048
        res = [start,value>>8,value&255]

        if(delay_usec > 0):
            sleep = delay_usec/1000000 - (time.perf_counter()-start)
            if(sleep > 0): self.sleep(sleep)

        return res
