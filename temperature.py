# The program reads a thermistor using a MCP3021 ADC and prints the temperature.
#
# The thermistor can be connected to either the top (Vcc) or bottom (ground) of the voltage divider.
# This defaults to bottom, but it can be changed with the -l option, which takes either 't' or 'b'.
#
# The -r option sets the thermistor base resistance. This defaults to 10000 or 10K.
# The -b option sets the thermistor B value. This defaults to 3950.
# The -v option sets the reference voltage. This defaults to 3.3V.
# The -d option sets the delay between readings. This defaults to 0.5 seconds.
# The I2C address can be set with the first argument. This defaults to 0x4A.

import argparse
import math
import smbus
import sys
import time

# Create the parser
parser = argparse.ArgumentParser(description='Reads the MCP3021 ADC and prints the temperature')

# Custom type function for thermistor base resistance
def resistance_type(x):
    try:
        if x[-1].upper() == 'K':
            return float(x[:-1]) * 1000
        return float(x)
    except ValueError:
        print(f"The thermistor base resistance {x} is an integer or floating point number greater than 0 or given in the form nK.")
        sys.exit(1)

# Custom type function for thermistor B value
def b_value_type(x):
    x = int(x)
    if x <= 0:
        print("The thermistor B value must be greater than 0.")
        sys.exit(1)
    return x

# Custom type function for I2C address
def i2c_address_type(x):
    try:
        return int(x, 16)
    except ValueError:
        print(f"The I2C address {x} is not a valid hex I2C address.")
        sys.exit(1)
        
# Custom type function for reference voltage
def vref_type(x):
    x = float(x)
    if x <= 0:
        print("The reference voltage must be greater than 0.")
        sys.exit(1)
    return x

# Custom type function for thermistor location
def location_type(x):
    x = x.lower()
    if x not in ['t', 'b']:
        print("The thermistor location must be either 't' (top - connected to Vcc) or 'b' (bottom - connected to ground).")
        sys.exit(1)
    return x

# Add the arguments
parser.add_argument('I2C_Address', metavar='Address', type=i2c_address_type, nargs='?', default='0x4A',
                    help='the I2C address in hex (default: 0x4A)')
parser.add_argument('-d', '--delay', type=float, default=0.5,
                    help='the delay in seconds between readings (default: 0.5)')
parser.add_argument('-v', '--vref', type=vref_type, default=3.3,
                    help='the reference voltage (default: 3.3V)')
parser.add_argument('-r', '--resistance', type=resistance_type, default=10000,
                    help='the thermistor base resistance (default: 10000 or 10K)')
parser.add_argument('-b', '--bvalue', type=b_value_type, default=3950,
                    help='the thermistor B value (default: 3950)')
parser.add_argument('-l', '--location', type=location_type, default='b',
                    help="the location of the thermistor - either 't' (top - connected to Vcc) or 'b' (bottom - connected to ground) (default: 'b')")

# Parse the arguments
args = parser.parse_args()

SLEEP_TIME = args.delay
I2C_ADDRESS = args.I2C_Address
ADC_BITS = 10
MAX_ADC_COUNT = pow(2, ADC_BITS) - 1
VREF = args.vref
THERMISTOR_BASE_RESISTANCE = args.resistance
COMPANION_RESISTANCE = 10000  # Ohms. The other resistor in the voltage divider.
T0 = 298.15  # Reference temperature in Kelvin
B_VALUE = args.bvalue  # Thermistor B value
THERMISTOR_ON_BOTTOM = args.location == 'b'

print(f"I2C address {hex(I2C_ADDRESS)[:2] + hex(I2C_ADDRESS)[2:].upper()}, Vref {VREF}V, Termistor on {'bottom' if THERMISTOR_ON_BOTTOM else 'top'}")
print(f"Thermistor base resistance {THERMISTOR_BASE_RESISTANCE} Ohms, B value {B_VALUE}")
print("Time\tADC\tVoltage\tResist\tTemperature")

bus = smbus.SMBus(1) # RPi revision 2 (0 for revision 1)
i2c_address = 0x49  # default address
t = 0
while True:
    try:
        # Reads word (2 bytes) as int
        rd = bus.read_word_data(I2C_ADDRESS, 0)
    except OSError as e:
        print(f"There is no I2C device present at {hex(I2C_ADDRESS)[:2] + hex(I2C_ADDRESS)[2:].upper()}.")
        sys.exit(1)
    # Exchanges high and low bytes
    data = ((rd & 0xFF) << 8) | ((rd & 0xFF00) >> 8)
    # Ignores two least significiant bits
    data = data >> 2

    # Calculate the voltage at the ADC input
    v = data * VREF / MAX_ADC_COUNT

    # Calculate the thermistor resistance
    if THERMISTOR_ON_BOTTOM:
        Rt = COMPANION_RESISTANCE / ((VREF / v) - 1)
    else:
        Rt = COMPANION_RESISTANCE * ((VREF / v) - 1)

    # Calculate the temperature in Kelvin
    T = 1 / (1/T0 + 1/B_VALUE * math.log(Rt/THERMISTOR_BASE_RESISTANCE))

    # Convert the temperature to Celsius
    temperature = T - 273.15

    print(f"{t:3.1f}\t{data}\t{v:.2f}V\t{Rt:.0f}\t{temperature:.1f}C")

    t += SLEEP_TIME
    time.sleep(SLEEP_TIME)

