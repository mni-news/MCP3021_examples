# MCP3021_examples

Python examples of 2 different ways to read MCP3021 ADC on a Raspberry Pi, and another program which reads an NTC thermistor with the MCP3021 and prints the temperature.

One example uses the smbus library to read the MCP3021, and the other example reads from /dev/i2c-1.
Both of this print the value periodically and take the following command line parameter:

* -d seconds between readings. The delay can be a floating point number for fractional seconds, but defaults to 0.5 seconds.
* -v the ADC reference voltage, which is VDD on the MCP3021. This defaults to 3.3V
* The I2C address is in hex without a leading "0x", e.g. "4a"

An example command line is:

`python mcp3021_smbus.py -d 0.25 -v 3.0 4c`

The program that prints the temperature takes these paramters and a few more

* -r the thermistor base resistance. The value can be given as a floating point number or as xK or x.yK. Defaults to 10K. 
* -b the thermistor beta value. Defaults to 3950.
* -l the thermistor location in the resistor divider, either t (top) connected to Vcc or b (bottom) connected to ground. Defaults to b.

An example command line is:

`python temperature.py -r 4.7K -b 3892 -l t 4b`