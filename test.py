import currentreader

reader = currentreader.CurrentReader(voltage=230)

reader.readChannel(chan=0,ampFactor=0.00281,ampExponent=1,ampMinimum=0)
print(reader.lastPower())

