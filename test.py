import currentreader

reader = currentreader.CurrentReader(ampFactor=0.0026,ampExponent=1.01,ampMinimum=0.015,voltage=230)

while(True):
    reader.readChannel(0)
    print("Current: {0}".format(reader.lastCurrent()))
    print("Power: {0}".format(reader.lastPower()))
