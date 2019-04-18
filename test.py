import currentreader

reader = currentreader.CurrentReader(voltage=230)
#print("Channel?")
#chan = int(input())
reader.readChannel(0,ampFactor=0.00285,ampExponent=1,ampMinimum=0)
chan0 = reader.lastPower()
reader.readChannel(1,ampFactor=0.00285,ampExponent=1,ampMinimum=0)
chan1 = reader.lastPower()
reader.readChannel(2,ampFactor=0.00285,ampExponent=1,ampMinimum=0)
chan2 = reader.lastPower()
reader.readChannel(3,ampFactor=0.00285,ampExponent=1,ampMinimum=0)
chan3 = reader.lastPower()

print(chan0+chan1+chan2-chan3)
