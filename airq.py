import board
import digitalio
import busio
import time
import adafruit_bme280
import adafruit_ccs811
import qwiic_tmp117
import IQR
import time
import sys
import _thread
import statistics as stat


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
class airq(object):
  _deviceErrors = { \
    1 << 5 : "HeaterSupply",  \
      1 << 4 : "HeaterFault", \
      1 << 3 : "MaxResistance", \
      1 << 2 : "MeasModeInvalid",  \
      1 << 1 : "ReadRegInvalid", \
      1 << 0 : "MsgInvalid" \
  }


  def __init__(self, ccs811_address=0x5b, bme280_address=0x77, tmp117_address=0x48, ccs811_n_samples=1):
    self.lock = _thread.allocate_lock()
    self.ccs811_n_samples = ccs811_n_samples

    self.i2c = busio.I2C(board.SCL, board.SDA)

    self.bme280 = adafruit_bme280.Adafruit_BME280_I2C(self.i2c, address=bme280_address)
    self.ccs811 = adafruit_ccs811.CCS811(self.i2c, address=ccs811_address)
    self.tmp117 = qwiic_tmp117.QwiicTmp117(address=tmp117_address)

    self.tmp117.begin()
    # The conversion and averaging affect who long we will have to wait
    # for a conversion. See the TMP117 data sheet.
    self.tmp117.set_avg(qwiic_tmp117.QwiicTmp117.CONV_AVG_8)
    self.tmp117.set_cycle(qwiic_tmp117.QwiicTmp117.CONV_CYCLE_2)

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
      self.read_tmp117()
      self.read_ccs811()
      self.lock.release()
      time.sleep(2)

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

    tvoc = self.queue_avg(self.tvoc_q, "tvoc")
    retval["tvoc_ppb"] = "{:.2f}".format(tvoc[0])
    retval["tvoc_std"] = "{:.2f}".format(tvoc[2])

    eco2 = self.queue_avg(self.eco2_q, "eco2")
    retval["eco2_ppm"] = "{:.2f}".format(eco2[0])
    retval["eco2_std"] = "{:.2f}".format(eco2[2])

    retval["pres_mb"] = "{:.2f}".format(self.queue_avg(self.pres_q, "pres", do_iqr=False)[0])

    retval["tdry_degc"] = "{:.2f}".format(self.queue_avg(self.tdry_q, "tdry", do_iqr=False)[0])

    retval["rh"] = "{:.2f}".format(self.queue_avg(self.rh_q, "rh", do_iqr=False)[0])

    retval["n"] = "{:d}".format(len(self.rh_q))

    self.lock.release()
    return retval

  def queue_add(self, q, val, param):
    q.append(val)
    if len(q) > self.ccs811_n_samples:
      q.pop(0)

  def queue_avg(self, q, name, do_iqr=True):
    """
    Return a tuple of the q:
      (median, mean, std dev)
    """
    if do_iqr:
      (cleaned, outliers) = IQR.iqr_filter(q, 5.0)
    else:
      cleaned = q
      outliers = []

    retval = (stat.median(cleaned), stat.mean(cleaned), stat.stdev(cleaned))

    if len(outliers):
      print(name, q)
      print("*** Ignoring outliers in", name, outliers)
      print(retval)

    return retval

  def read_bme280(self):
    self.rh = self.bme280.humidity
    #self.pres = self.bme280.pressure/100.0
    self.pres = self.bme280.pressure
    self.queue_add(self.rh_q, self.rh, "rh")
    self.queue_add(self.pres_q, self.pres, "pres")

  def read_tmp117(self):
    while not self.tmp117.is_ready():
      time.sleep(0.05)
    self.tdry = self.tmp117.temperature_celsius
    self.queue_add(self.tdry_q, self.tdry, "tdry")

  def read_ccs811(self):
    self.ccs811.set_environmental_data(self.rh, self.tdry)
    #while not self.ccs811.data_available():
    while not self.ccs811.data_ready:
      print("CCS811 starting up")
      time.sleep(1)

    if self.ccs811.data_ready:
      self.eco2 = self.ccs811.eco2
      self.tvoc = self.ccs811.tvoc
      self.queue_add(self.eco2_q, self.eco2, "eco2")
      self.queue_add(self.tvoc_q, self.tvoc, "tvoc")

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
    n_samples = 10
    if len(sys.argv) == 2:
      n_samples = int(sys.argv[1])

    device = airq(ccs811_n_samples=n_samples)
    while True:
      # Sleep first so that a full series can be collected
      time.sleep(n_samples)
      print(device.reading())
