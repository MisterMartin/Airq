import qwiic_ccs811
import qwiic_bme280
import time
import sys
import _thread


"""
CCS811

# pylint: disable=C0103
# pylint: disable=C0325
"""
"""
Sparkfun CCS881/BME280 Combo Board

Note: Sparkfun admits that the BME280 measurements will be
inaccurate due to its proximity to the hot CCS811 chip.
This class can be used with standalone CCS811 and BME280 
chips, just by specifying the I2C adddresses for them.

Code for this class was borrowed from the examples at
https://qwiic-ccs811-py.readthedocs.io/en/latest/?
"""
class ccs811_bme280(object):
  _deviceErrors = { \
    1 << 5 : "HeaterSupply",  \
      1 << 4 : "HeaterFault", \
      1 << 3 : "MaxResistance", \
      1 << 2 : "MeasModeInvalid",  \
      1 << 1 : "ReadRegInvalid", \
      1 << 0 : "MsgInvalid" \
  }


  def __init__(self, n_avg=60, ccs811_address=0x5b, bme280_address=0x77):
    self.lock = _thread.allocate_lock()
    self.n_avg = n_avg

    self.ccs811 = qwiic_ccs811.QwiicCcs811(address=ccs811_address)
    self.bme280 = bme280 = qwiic_bme280.QwiicBme280(address=bme280_address)

    self.ccs811.begin()
    self.bme280.begin()

    self.tvoc_q = []
    self.eco2_q = []
    self.pres_q = []
    self.tdry_q = []
    self.rh_q = []

    _thread.start_new_thread(self.read_loop, (None,))
    # Sleep so that the measure thread can start
    time.sleep(1)


  def read_loop(self, arg):
    while True:
      self.lock.acquire()
      self.read_bme280()
      self.read_ccs811()
      self.lock.release()
      time.sleep(1)

  def reading(self):
    """
    Return a hash containing sensor readings.
    The hash will contain:
        temp_C
        press_mb
        rh
    """
    self.lock.acquire()
    retval = {}
    retval["tvoc_ppb"] = "{:.2f}".format(self.queue_avg(self.tvoc_q))
    retval["eco2_ppm"] = "{:.2f}".format(self.queue_avg(self.eco2_q))
    retval["pres_mb"] = "{:.2f}".format(self.queue_avg(self.pres_q))
    retval["tdry_degc"] = "{:.2f}".format(self.queue_avg(self.tdry_q))
    retval["rh"] = "{:.2f}".format(self.queue_avg(self.rh_q))
    retval["n"] = "{:d}".format(len(self.tvoc_q))
    self.lock.release()
    return retval

  def queue_add(self, q, val):
    q.append(val)
    if len(q) > self.n_avg:
      q.pop(0)
    return q

  def queue_avg(self, q):
    return sum(q)/len(q)

  def read_bme280(self):

    self.rh = self.bme280.humidity
    self.tdry = self.bme280.temperature_celsius
    self.pres = self.bme280.pressure/100.0
    self.queue_add(self.rh_q, self.rh)
    self.queue_add(self.tdry_q, self.tdry)
    self.queue_add(self.pres_q, self.pres)


  def read_ccs811(self):
    self.ccs811.set_environmental_data(self.rh, self.tdry)
    while not self.ccs811.data_available():
      print("CCS811 starting up")
      time.sleep(1)

    if self.ccs811.data_available():
      self.ccs811.read_algorithm_results()
      self.eco2 = self.ccs811.CO2
      self.tvoc = self.ccs811.TVOC
      self.queue_add(self.eco2_q, self.eco2)
      self.queue_add(self.tvoc_q, self.tvoc)

    else:
      print("CCS811  data not avaiable")
      if self.ccs811.check_status_error():
        error = self.ccs811.get_error_register();
        if error == 0xFF:   
          # communication error
          print("CCS811 failed to get Error ID register from sensor")
        else:
          strErr = "CCS811 unknown error"
          for code in self._deviceErrors.keys():
            if error & code:
              strErr = self._deviceErrors[code]
              break
          print("CCS811 device error: %s" % strErr)

if __name__ == '__main__':
    sleep_int = 1
    if len(sys.argv) == 2:
      sleep_int = int(sys.argv[1])

    device = ccs811_bme280(n_avg=sleep_int)
    while True:
      # Sleep first so that a full series can be collected
      time.sleep(sleep_int)
      print(device.reading())
