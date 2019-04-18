import currentreader

reader = currentreader.CurrentReader(voltage=230)

reader.readChannel(chan=3,ampFactor=0.0025,ampExponent=1,ampMinimum=0)
print(reader.lastPower())

