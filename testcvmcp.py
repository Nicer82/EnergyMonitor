import time
import statistics
import math
import spidev

# Read settings
ADC_SAMPLESPERWAVE = 60 # If set to more then 400 with one channel, the code can't keep up, so that is about the max samples per wave
ADC_ACWAVESTOREAD = 250

# Mains properties
AC_FREQUENCY = 50

C_CALIBRATIONFACTOR = 0.01667
V_CALIBRATIONFACTOR = 0.2406
CALIBRATIONFACTOR = 0.003995

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

def readadc(channels):
    data = []
    
    for i in channels:
        data.append([])
        
    start = time.perf_counter()
    nextRead = start

    for i in range(ADC_SAMPLESPERWAVE*ADC_ACWAVESTOREAD):
        nextRead += 1/(ADC_SAMPLESPERWAVE*AC_FREQUENCY)

        # Read channels
        for ci in range(len(channels)):
            # Add a delay on the last channel to match timings. This is way more accurate than time.sleep() because it works up to the microsecond.
            if(ci == len(channels)-1):
                delay = max([0,round((nextRead-time.perf_counter())*1000000)]) 
            else:
                delay = 0

            response = spi.xfer2([6+((4&channels[ci])>>2),(3&channels[ci])<<6,0],2000000,delay)
            data[ci].append(((response[1] & 15) << 8) + response[2])

    end = time.perf_counter()

    for i in range(len(data[0])):
        print("{};{}".format(data[0][i],data[1][i]))

    #print("Reads: {}, Performance: {} sps, Requested time: {} ms, Actual time: {} ms".format(len(data[0]),len(data[0])/(end-start),1000/AC_FREQUENCY*ADC_ACWAVESTOREAD,(end-start)*1000))
    
    return data

def flowdirection(datac,datav):
    total = 0
    
    for i in range(len(datac)):
        total += datac[i]*datav[i]
    
    if total != 0:
        return total/abs(total)
    
    return 0

# Create the SPI
spi = spidev.SpiDev()
spi.open(0,0)

channels = [0,1,2,3,4,5]

while(True):
    data = readadc(channels)
    datac1 = data[0]
    datav1 = data[1]
    datac2 = data[2]
    datav2 = data[3]
    datac3 = data[4]
    datav3 = data[5]
    
    #print("Current data: Before normalize: Reads: {}, Min: {}, Max: {}".format(len(datac),min(datac),max(datac)))
    #print("Voltage data: Before normalize: Reads: {}, Min: {}, Max: {}".format(len(datav),min(datav),max(datav)))

    datac1 = normalize(datac1)
    datav1 = normalize(datav1)
    datac2 = normalize(datac2)
    datav2 = normalize(datav2)
    datac3 = normalize(datac3)
    datav3 = normalize(datav3)
    
    #print("Current data: After normalize: Reads: {}, Min: {}, Max: {}".format(len(datac),min(datac),max(datac)))
    #print("Voltage data: After normalize: Reads: {}, Min: {}, Max: {}".format(len(datav),min(datav),max(datav)))

    voltage1 = rootmeansquare(datav1) * V_CALIBRATIONFACTOR
    current1 = rootmeansquare(datac1) * flowdirection(datac1,datav1) * C_CALIBRATIONFACTOR
    voltage2 = rootmeansquare(datav2) * V_CALIBRATIONFACTOR
    current2 = rootmeansquare(datac2) * flowdirection(datac2,datav2) * C_CALIBRATIONFACTOR
    voltage3 = rootmeansquare(datav3) * V_CALIBRATIONFACTOR
    current3 = rootmeansquare(datac3) * flowdirection(datac3,datav3) * C_CALIBRATIONFACTOR
    
    ### Power calculation
    datacv1 = []
    for i in range(len(datac1)):
        datacv1.append(datac1[i] * datav1[i])
    
    datacv2 = []
    for i in range(len(datac2)):
        datacv2.append(datac2[i] * datav2[i])
    
    datacv3 = []
    for i in range(len(datac3)):
        datacv3.append(datac3[i] * datav3[i])
        
    power1 = statistics.mean(datacv1)*CALIBRATIONFACTOR;
    power2 = statistics.mean(datacv2)*CALIBRATIONFACTOR;
    power3 = statistics.mean(datacv3)*CALIBRATIONFACTOR;
    
    print("L1: Current: {} A, Voltage: {} V, Power: {} W".format(round(current1,3),round(voltage1,1),round(power1)))
    print("L2: Current: {} A, Voltage: {} V, Power: {} W".format(round(current2,3),round(voltage2,1),round(power2)))
    print("L3: Current: {} A, Voltage: {} V, Power: {} W".format(round(current2,3),round(voltage3,1),round(power3)))
    print("Total: Current: {} A, Voltage: {} V, Power: {} W".format(round(current1+current2+current3,3),round(statistics.mean([voltage1,voltage2,voltage3]),1),round(power1+power2+power3)))

spi.close()
