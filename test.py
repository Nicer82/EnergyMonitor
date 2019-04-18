import currentreader

reader = currentreader.CurrentReader(voltage=230)
print("Channel?")
chan = int(input())
reader.readChannel(chan,ampFactor=0.00285,ampExponent=1,ampMinimum=0)
print(reader.lastPower())

