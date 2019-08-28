# Stub for SpiDev on RPI returning random results
import time
import random

class SpiDev:
    def open(self, bus, device):
        return
    def xfer2(self, values, speed_hz = 0, delay_usec = 0, bits_per_word = 8):
        start = time.perf_counter()
        
        res = [0,round(random.random()*pow(2,bits_per_word)),round(random.random()*pow(2,bits_per_word))]

        if(delay_usec > 0):
            sleep = delay_usec/1000000 - (time.perf_counter()-start)
            if(sleep > 0): time.sleep(sleep)

        return res
