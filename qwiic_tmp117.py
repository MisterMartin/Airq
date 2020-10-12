#-----------------------------------------------------------------------------
from __future__ import print_function
import math
import time
import qwiic_i2c

# Define the device name and I2C addresses. These are set in the class defintion
# as class variables, making them avilable without having to create a class instance.
# This allows higher level logic to rapidly create a index of qwiic devices at
# runtine
#
# The name of this device
_DEFAULT_NAME = "Qwiic TMP117"

# Some devices have multiple availabel addresses - this is a list of these addresses.
# NOTE: The first address in this list is considered the default I2C address for the
# device.
_AVAILABLE_I2C_ADDRESS = [0x48, 0x49, 0x4a, 0x4b]

# Default Setting Values
_settings = {"conversionMode" : 0,         \
            "avgMode"  : 1
            }

# define our valid chip IDs
_validChipIDs = [0x117]

# define the class that encapsulates the device being created. All information associated with this
# device is encapsulated by this class. The device class should be the only value exported
# from this module.

class QwiicTmp117(object):
    """
    QwiicTmp117

        :param address: The I2C address to use for the device.
                        If not provided, the default address is used.
        :param i2c_driver: An existing i2c driver object. If not provided
                        a driver object is created.
        :return: The TMP117 device object.
        :rtype: Object
    """
    # Constructor
    device_name         =_DEFAULT_NAME
    available_addresses = _AVAILABLE_I2C_ADDRESS

    # mode flags for the device - user exposed

    # Register names for the TMP117
    TMP117_TEMPERATURE_REG = 0x00
    TMP117_CONFIG_REG      = 0x01
    TMP117_CHIP_ID_REG     = 0x0f
    
    CONFIG_READY_BIT   = 13
    CONFIG_MODE_BIT    = 10
    CONFIG_CYCLE_BIT   = 7
    CONFIG_AVG_BIT     = 5
    CONFIG_RESET_BIT   = 1

    CONFIG_READY_MASK = 0b1  << CONFIG_READY_BIT
    CONFIG_MODE_MASK  = 0b11  << CONFIG_MODE_BIT
    CONFIG_CYCLE_MASK = 0b111 << CONFIG_CYCLE_BIT
    CONFIG_AVG_MASK   = 0b11  << CONFIG_AVG_BIT

    MODE_CONTINUOUS = 0b00 << CONFIG_MODE_BIT
    MODE_SHUTDOWN   = 0b01 << CONFIG_MODE_BIT
    MODE_ONESHOT    = 0b11 << CONFIG_MODE_BIT

    CONV_AVG_NONE = 0 << CONFIG_AVG_BIT
    CONV_AVG_8    = 1 << CONFIG_AVG_BIT
    CONV_AVG_32   = 2 << CONFIG_AVG_BIT
    CONV_AVG_64   = 3 << CONFIG_AVG_BIT

    CONV_CYCLE_0 = 0 << CONFIG_CYCLE_BIT
    CONV_CYCLE_1 = 1 << CONFIG_CYCLE_BIT
    CONV_CYCLE_2 = 2 << CONFIG_CYCLE_BIT
    CONV_CYCLE_3 = 3 << CONFIG_CYCLE_BIT
    CONV_CYCLE_4 = 4 << CONFIG_CYCLE_BIT
    CONV_CYCLE_5 = 5 << CONFIG_CYCLE_BIT
    CONV_CYCLE_6 = 6 << CONFIG_CYCLE_BIT
    CONV_CYCLE_7 = 7 << CONFIG_CYCLE_BIT

    # degC / bit
    TEMP_RESOLUTION_DEGC = 7.8125e-3

    # Constructor
    def __init__(self, address=None, i2c_driver=None):

        # Did the user specify an I2C address?
        self.address = self.available_addresses[0] if address is None else address

        # load the I2C driver if one isn't provided

        if i2c_driver is None:
            self._i2c = qwiic_i2c.getI2CDriver()
            if self._i2c is None:
                print("Unable to load I2C driver for this platform.")
                return
        else:
            self._i2c = i2c_driver

    # ----------------------------------
    # is_connected()
    #
    # Is an actual board connected to our system?

    def is_connected(self):
        """
            Determine if a TMP117 device is conntected to the system..

            :return: True if the device is connected, otherwise False.
            :rtype: bool

        """
        return qwiic_i2c.isDeviceConnected(self.address)

    connected = property(is_connected)

    # ----------------------------------
    # begin()
    #
    # Initialize the system/validate the board.
    def begin(self):
        """
            Initialize the operation of the TMP117 module.

            The conversion cyle will be set to 4, and the averaging to 8. This
            results in a value being available once per second.

            Change these values if faster readings are needed. See Table 7 in the 
            TMP117 data sheet.

            :return: Returns true of the initializtion was successful, otherwise False.
            :rtype: bool

        """
        # are we who we need to be?
        chipID = self.get_reg(self.TMP117_CHIP_ID_REG)
        if chipID not in _validChipIDs:
            print("Invalid Chip ID: 0x%.2X" % chipID)
            return False

        self.reset()
        self.set_mode(self.MODE_CONTINUOUS)
        self.set_cycle(self.CONV_CYCLE_4)
        self.set_avg(self.CONV_AVG_8)

        return True

    def get_reg(self, reg):
      value = self._i2c.readWord(self.address, reg)
      value = ((value & 0xff) << 8) | ((value >> 8) & 0xff)
      #print("Register {0} is: {1:016b}".format(reg, value))
      return value

    def set_reg(self, reg, value):
      #print("Writing register {0} with: {1:016b}".format(reg, value))
      value = ((value & 0xff) << 8) | ((value >> 8) & 0xff)
      self._i2c.writeWord(self.address, reg, value)
      self.get_reg(reg)

    def set_mode(self, mode):
        """
            Set the operational mode of the sensor.

            :param mode: One of the class constant values.
                  MODE_CONTINUOUS
                  MODE_SHUTDOWN
                  MODE_ONESHOT

            :return: No return value

        """

        if mode > 0b11:
            mode = MODE_SHUTDOWN  # Error check. Default to shutdown mode
            print("Illegal TMP117 mode selected (", mode, "), device placed in shutdown mode.")

        config = self.get_reg(self.TMP117_CONFIG_REG)
        config &=  ~self.CONFIG_MODE_MASK
        config |=   mode
        self.set_reg(self.TMP117_CONFIG_REG, config)

    def get_mode(self):
        """
            Returns the operational mode of the sensor.

            :return: The current operational mode
            :rtype: MODE_CONTINUOUS, MODE_SHUTDOWN, MODE_ONESHOT

        """
        config = self.get_reg(self.TMP117_CONFIG_REG)
        config = config & self.CONFIG_MODE_MASK
        return config

    mode = property(get_mode, set_mode)

    def set_cycle(self, cycleSetting):
        """
        Set the conversion cycle bits in the TMP117s config register

        :param cycleSetting: The conversion cycle bits for the TMP117. Acceptable values
          CONV_CYCLE_0 = 0
          CONV_CYCLE_1 = 1
          CONV_CYCLE_2 = 2
          CONV_CYCLE_3 = 3
          CONV_CYCLE_4 = 4
          CONV_CYCLE_5 = 5
          CONV_CYCLE_6 = 6
          CONV_CYCLE_7 = 7

        :return: No return value

        """
        config = self.get_reg(self.TMP117_CONFIG_REG)
        config &= ~self.CONFIG_CYCLE_MASK
        config |= cycleSetting
        self.set_reg(self.TMP117_CONFIG_REG, config)

    def get_cycle(self):
        """
        Get the conversion cycle bits in the TMP117s config register

        :return: The cycle value

        """

        cycle = self.get_reg(self.TMP117_CONFIG_REG)
        cycle &= self.CONFIG_CYCLE_MASK
        return cycle

    cycle = property(get_cycle, set_cycle)

    def set_avg(self, avgSetting):
        """
        Set the avg bits in the TMP117s config register

        :param avgSetting: The avg bits for the TMP117. Acceptable values
           CONV_AVG_NONE = no averaging
           CONV_AVG_8 = 8 averaged conversions
           CONV_AVG_32 = 32 averaged conversions
           CONV_AVG_64 = 64 averaged conversions

        :return: No return value

        """
        config = self.get_reg(self.TMP117_CONFIG_REG)
        config &= ~ self.CONFIG_AVG_MASK
        config |= avgSetting
        self.set_reg(self.TMP117_CONFIG_REG, config)

    def get_avg(self):
        """
        Get the avg bits in the TMP117s config register

        :return: The avg value
        """

        avg = self.get_reg(self.TMP117_CONFIG_REG)
        avg &= self.CONFIG_AVG_MASK
        return avg

    average = property(get_avg, set_avg)

    # pylint: enable=no-self-use
    # Check the ready bit and return true if temperature is avaiable.
    def is_ready(self):
        """
        Return if temperature is available

        :return: True if temperature is available
        :rvalue: boolean
        """

        ready = self.get_reg(self.TMP117_CONFIG_REG)
        return  True if ready & self.CONFIG_READY_MASK else False

    # Strictly resets.  Run .begin() afterwards
    def reset(self):
        """
        Resets the sensor. If called, the begin method must be called before
        using the sensor.

        """
        self.set_reg(self.TMP117_CONFIG_REG, 0x1 << self.CONFIG_RESET_BIT)

    def twos_complement(self, value, bitWidth):
      """
      Returns the twos complement value for a number of a specified bit width.
      Note that 2^bits - 1 >= val >= 0 is required.

      :param value: The number to be converted.
      :param bitWidth: The bit width of the number.

      :return The two's complment value.
      :rtype int
      """
      if value >= 2**bitWidth:
          # This catches when someone tries to give a value that is out of range
          raise ValueError("Value: {} out of range of {}-bit value.".format(value, bitWidth))
      else:
          return value - int((value << 1) & 2**bitWidth)

    def get_temperature_celsius(self):
        """
        Returns temperature in DegC. NOTE THAT READING THE TEMPERATURE WILL RESET THE READY STATUS.

        :return: The current temperature in C.
        :rtype: float
        """
        #  Returns temperature in DegC, resolution is 0.01 DegC. Output value of "5123" equals 51.23 DegC.
        #  t_fine carries fine temperature as global value

        # get the reading (adc_T);

        temp_value = self.get_reg(self.TMP117_TEMPERATURE_REG)

        temp_c = self.TEMP_RESOLUTION_DEGC * self.twos_complement(temp_value, 16)

        return temp_c

    temperature_celsius = property(get_temperature_celsius)

    def get_temperature_fahrenheit(self):
        """
        Returns temperature in Deg F, resolution is 0.01 DegF. Output value of "5123" equals 51.23 DegF.
         t_fine carries fine temperature as global value

        :return: The current temperature in F.
        :rtype: float
        """
        output = self.temperature_celsius
        return (output * 9) / 5 + 32

    temperature_fahrenheit = property(get_temperature_fahrenheit)

if __name__ == '__main__':
  device = QwiicTmp117()
  device.begin()
  device.set_avg(QwiicTmp117.CONV_AVG_8)
  device.set_cycle(QwiicTmp117.CONV_CYCLE_2)
  print("Mode is {0:016b}".format(device.mode))
  print("Conversion cycle is {0:016b}".format(device.cycle))
  print("Conversion average is {0:016b}".format(device.average))  

  while True:
    if device.is_ready():
      print(device.temperature_celsius)
    else:
      time.sleep(0.05)