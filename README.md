# Airq
Air quality to CHORDS

## Setup
Enable I2C using raspi-config

        sudo raspi-config

Enable I2C clock stretching by setting the I2C baud rate in `/boot/config.txt`:

        dtparam=i2c_arm_baudrate=10000

Install packages:

        sudo apt-get install i2c-tools
        sudo apt-get install libatlas-base-dev
Install chip support:

        # Install the sparkfun qwiic python support
        sudo pip3 install sparkfun-qwiic

Python packages:
    pip3 install numpy

## Testing
Verify that both chips are there:
```
sudo i2cdetect -y 1
sudo: unable to resolve host airq
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- 5b -- -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- -- 77
```

Verify the combo card:

    python ccs811_bme280.py
    CCS811 starting up
    CCS811 starting up
    CCS811 starting up
    CCS811 starting up
    {'rh': '22.70', 'tdry_degc': '25.91', 'eco2_ppm': '400.00', 'pres_mb': '858.09', 'tvoc_ppb': '0.00'}
    {'rh': '21.82', 'tdry_degc': '25.98', 'eco2_ppm': '400.00', 'pres_mb': '857.37', 'tvoc_ppb': '0.00'}
    {'rh': '21.85', 'tdry_degc': '25.93', 'eco2_ppm': '415.00', 'pres_mb': '857.92', 'tvoc_ppb': '2.00'}
    {'rh': '21.82', 'tdry_degc': '25.98', 'eco2_ppm': '415.00', 'pres_mb': '857.43', 'tvoc_ppb': '2.00'}
    {'rh': '21.80', 'tdry_degc': '25.93', 'eco2_ppm': '415.00', 'pres_mb': '857.86', 'tvoc_ppb': '2.00'}
    {'rh': '21.82', 'tdry_degc': '25.98', 'eco2_ppm': '418.00', 'pres_mb': '857.44', 'tvoc_ppb': '2.00'}
    {'rh': '21.91', 'tdry_degc': '25.95', 'eco2_ppm': '418.00', 'pres_mb': '857.62', 'tvoc_ppb': '2.00'}

## Resources

- Sparkfun python docs for the [BME280](https://qwiic-bme280-py.readthedocs.io/en/latest/?)
- Sparkfun python docs for the [CCS811](https://qwiic-ccs811-py.readthedocs.io/en/latest/?)
- Sparkfun [CCS811 hookup guide](https://learn.sparkfun.com/tutorials/ccs811bme280-qwiic-environmental-combo-breakout-hookup-guide?_ga=2.42719461.1539937089.1601160436-1748549399.1600881830).
- Sparkfun [GitHub CCS811 repository](https://github.com/sparkfun/CCS811_Air_Quality_Breakout).
- Sparkfun [Qwicc-shim](https://learn.sparkfun.com/tutorials/qwiic-shim-for-raspberry-pi-hookup-guide?_ga=2.122920139.1539937089.1601160436-1748549399.1600881830).
- Note about the chip [not being supported on rPi](https://raspberrypi.stackexchange.com/questions/74418/pi-cannot-communicate-with-i2c-sensor) :-(. But it can be ameliorated by slowing down the I2C bus.
- Interquartile Range Filtering:
    - https://en.wikipedia.org/wiki/Interquartile_range
    - https://machinelearningmastery.com/how-to-use-statistics-to-identify-outliers-in-data/
