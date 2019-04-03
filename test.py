import currentreader

reader = currentreader.CurrentReader(voltage=230)

while(True):
    reader.readChannel(chan=0,ampFactor=0.0026,ampExponent=1.018,ampMinimum=0.015)
    print("Current: {0}".format(reader.lastCurrent()))
    print("Power: {0}".format(reader.lastPower()))
