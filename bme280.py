"""
BME280 (I2C) abstraction
"""
import board
import busio
import adafruit_bme280

# pylint: disable=C0103
# pylint: disable=C0325

class bme280(object):
    """
    Interface with an I2C connect BME280 sensor.
    """
    def __init__(self):
      self.i2c = busio.I2C(board.SCL, board.SDA)
      self.bme280 = adafruit_bme280.Adafruit_BME280_I2C(self.i2c)

    def reading(self):
        """
        Return a hash containing sensor readings.
        The hash will contain:
           temp_C
           press_mb
           rh
        """
        retval = {}
        retval["temp_C"] = "{:.2f}".format(self.bme280.temperature)
        retval["pres_mb"] = "{:.2f}".format(self.bme280.pressure/100)
        retval["rh"] = "{:.2f}".format(self.bme280.humidity)
        return retval

if __name__ == '__main__':
    bme280 = bme280()
    print(bme280.reading())
