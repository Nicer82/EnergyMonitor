import state
import time

s = state.State()

statepointdata = {
  "time": time.time(),
  "l1_current": 1.123,
  "l1_voltage": 240.1,
  "l1_power": 269.6323,
  "l2_current": 1.321,
  "l2_voltage": 240.2,
  "l2_power": 317.3042,
  "l3_current": 1.231,
  "l3_voltage": 240.3,
  "l3_power": 295.8093,
  "total_current": 3.675,
  "total_voltage": 240.2,
  "total_power": 882.7458
}
s.registerState('test',statepointdata)
