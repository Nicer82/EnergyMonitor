import state
import time
import random

s = state.State()

input = {
  "point": "test",
  "brown": {
    "current": -1.123,
    "voltage": 240.1,
    "power": -269.6323
  },
  "black": {
    "current": -1.321,
    "voltage": 240.2,
    "power": -317.3042
  },
  "gray": {
    "current": -1.231,
    "voltage": 240.3,
    "power": -295.8093
  },
  "current": -3.675,
  "voltage": 240.2,
  "power": -882.7458
}
while(True):
  input["time"] = time.time()
  s.registerState(input.copy())
  time.sleep(random.random()*3+1)
