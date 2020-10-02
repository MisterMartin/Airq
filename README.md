# AirQ

## Air Quality to CHORDS

A Raspberry Pi system which makes some rudimentary air quailty measurements, and sends them
to a CHORDS portal. The _ccs811_bme280.py_ module can be used by itself, without connecting
to CHORDS.

This is based on the CCS811 sensor, which produces a relative reading of Total Volatile Organic Compounds (TVOC).
This sensor is targeted for use in unsophisticated HVAC applications, for automatic control of ventilation.
It seems to have a lot of quirks and mysteries; it's hard to find any definitive description of how it
works, and what to expect in a real-world application. 

The CCS811 uses a heated metal oxide sensor. The sensor is subject to drift, must be conditioned, and referenced
to a changinging baseline value. These functions are performed by an onboard processor, running an algorithm
that tries to automate the process continuously. The algorithm is not very well documented, but you 
can get a sense of how it is working from the application notes.

The CCS811 also provides a value for "equivalent CO2", eCO2. The rationale is that since humans emit
VOCs, when the TVOC increases, there must be humans present, and the CO2 concentration must be
increasing. You can see that when the sensor is powered up, it starts with a value of eCO2 of
400ppm, and then adjusts it based on the behavior of TVOC. There is no documentation
on this algorithm. This all seems pretty tenuous but perhaps it has some value to the
HVAC industry.

So, my _personal_ observations are:

* The sensor will tell you something about TVOC, in an indoor environment.
* Do not expect an absolute reading.
* Due to the internal baselining, done on who-knows-what schedule,
  even the relative readings probably should probably not be compared from day to.
  One application note says that this is done every 24 hours, and uses the lowest
  reading over that period. But it seems that you would see a jump every 24 hours
  as it is adjusted, and we don't see that. Perhaps it is done continuously?
* The relative TVOC behavior over time is the most useful aspect of the readings. It clearly
  picks up cooking, and proximity of TVOC outgassing objects (e.g. set a lime near it, and it
  senses it immediately).
* The eCO2 proxy seems really bogus as an air quality indicator, since there are so many things
  in the home that can have very large impacts on TVOC. eCO2 seems to basically track
  TVOC. Perhaps it would be an indicator for spaces that only have humans as sources of TVOCs. I don't know.
* But, _it is still fun and interesting to ponder what the readings mean_ in my
  particular application.

It is hard to find any solidly documented results from this sensor. It seems to
be mostly the plaything of makers and tinkerers (like myself). I'll document
real-world usage data here as I find it:

* [A long disussion](https://github.com/maarten-pennings/CCS811/issues/8) between several users,
  with some actual data.

Application notes and data sheets are in the _Docs_ directory.

## Setup on Raspberry Pi Zero W

1. Install Raspberry Pi OS using the [Raspberry Pi Imager](https://www.raspberrypi.org/downloads/).

1. ...

1. Enable I2C using raspi-config

        sudo raspi-config

1. Enable I2C clock stretching by setting the I2C baud rate in `/boot/config.txt`:

        dtparam=i2c_arm_baudrate=10000

1. Install packages:

        sudo apt-get install i2c-tools
        sudo apt-get install libatlas-base-dev

1. Install chip support:

        # Install the sparkfun qwiic python support
        sudo pip3 install sparkfun-qwiic

1. Python packages:

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

    python3 ccs811_bme280.py
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
