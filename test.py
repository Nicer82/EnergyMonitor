import currentreader

reader = currentreader.CurrentReader(voltage=230)

reader.readChannel(chan=0,ampFactor=0.00282,ampExponent=1,ampMinimum=0)
print(reader.lastPower())

