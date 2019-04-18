import currentreader

reader = currentreader.CurrentReader(voltage=1)

for i in range(10):
  reader.readChannel(chan=0,ampFactor=1,ampExponent=1,ampMinimum=0,cycle=i)
  print("{0};{1};{2}".format(i,0,reader.lastPower()))
  reader.readChannel(chan=1,ampFactor=1,ampExponent=1,ampMinimum=0,cycle=i)
  print("{0};{1};{2}".format(i,1,reader.lastPower()))
  reader.readChannel(chan=2,ampFactor=1,ampExponent=1,ampMinimum=0,cycle=i)
  print("{0};{1};{2}".format(i,2,reader.lastPower()))
  reader.readChannel(chan=3,ampFactor=1,ampExponent=1,ampMinimum=0,cycle=i)
  print("{0};{1};{2}".format(i,3,reader.lastPower()))
  
