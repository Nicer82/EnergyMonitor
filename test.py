import currentreader

reader = currentreader.CurrentReader(voltage=1)

for i in range(10):
  reader.readChannel(chan=0,ampFactor=1,ampExponent=1,ampMinimum=0,cycle=i)
  print("{0};{1};{2};{3}".format(i,0,500,reader.lastPower()))
  reader.readChannel(chan=1,ampFactor=1,ampExponent=1,ampMinimum=0,cycle=i)
  print("{0};{1};{2};{3}".format(i,1,500,reader.lastPower()))
  reader.readChannel(chan=2,ampFactor=1,ampExponent=1,ampMinimum=0,cycle=i)
  print("{0};{1};{2};{3}".format(i,2,500,reader.lastPower()))
  reader.readChannel(chan=3,ampFactor=1,ampExponent=1,ampMinimum=0,cycle=i)
  print("{0};{1};{2};{3}".format(i,3,500,reader.lastPower()))
