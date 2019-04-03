import currentreader

reader = currentreader.CurrentReader(ampFactor=0.002667,ampMinimum=0.015,voltage=230)

while(True):
    reader.readChannel(0)
    print("Current: {0}".format(reader.lastCurrent()))
    print("Power: {0}".format(reader.lastPower()))
