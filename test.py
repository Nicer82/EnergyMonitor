import currentreader

reader = currentreader.CurrentReader(voltage=230)
print("Channel?")
chan = input()
reader.readChannel(chan,ampFactor=0.00282,ampExponent=1,ampMinimum=0)
#print(reader.lastPower())

