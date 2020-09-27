# Airq
Air quality to CHORDS

## Setup
Enable I2C using raspi-config

        sudo raspi-config

Enable I2C clock stretching by setting the I2C baud rate in `/boot/config.txt`:

        dtparam=i2c_arm_baudrate=10000

Install i2c tools:

        sudo apt-get install i2c-tools

Install chip support:

        # Install the sparkfun qwiic python support
        sudo pip3 install sparkfun-qwiic

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

Verify the BME280:

        python3 bme280.py

Verify the CCS811:

        python ccs811.py

## Resources

- Sparkfun python docs for the [BME280](https://qwiic-bme280-py.readthedocs.io/en/latest/?)
- Sparkfun python docs for the [CCS811](https://qwiic-ccs811-py.readthedocs.io/en/latest/?)
- Sparkfun [CCS811 hookup guide](https://learn.sparkfun.com/tutorials/ccs811bme280-qwiic-environmental-combo-breakout-hookup-guide?_ga=2.42719461.1539937089.1601160436-1748549399.1600881830).
- Sparkfun [GitHub CCS811 repository](https://github.com/sparkfun/CCS811_Air_Quality_Breakout).
- Sparkfun [Qwicc-shim](https://learn.sparkfun.com/tutorials/qwiic-shim-for-raspberry-pi-hookup-guide?_ga=2.122920139.1539937089.1601160436-1748549399.1600881830).
- Note about the chip [not being supported on rPi](https://raspberrypi.stackexchange.com/questions/74418/pi-cannot-communicate-with-i2c-sensor) :-(.