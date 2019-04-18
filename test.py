import currentreader

reader = currentreader.CurrentReader(voltage=1)

reader.readChannel(chan=3,ampFactor=1,ampExponent=1,ampMinimum=0)
