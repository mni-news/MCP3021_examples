# This program is an exmaple of reading the MCP3021 ADC using the smbus library
# The program reads the ADC value and converts it to voltage
# The first byte contains the 4 most significant bits of the ADC value and
# the second byte contains the 6 least significant bits of the ADC value
# as the 6 most significant bits of that byte.)
#
#        0 0 0 0 D9 D8 D7 D6     D5 D4 D3 D2 D1 D0 0 0
#
# The I2C address is on bus 1 (from i2cdetect -y 1)

import argparse
import smbus
import sys
import time

# Create the parser
parser = argparse.ArgumentParser(description='Reads the MCP3021 ADC using the smbus library')

# Add the arguments
parser.add_argument('I2C_Address', metavar='Address', type=str, nargs='?', default='0x4A',
                    help='the I2C address in hex (default: 0x4A)')
parser.add_argument('-d', '--delay', type=float, default=0.5,
                    help='the delay in seconds between readings (default: 0.5)')
parser.add_argument('-v', '--vref', type=float, default=3.3,
                    help='the reference voltage (default: 3.3V)')

# Parse the arguments
args = parser.parse_args()

SLEEP_TIME = args.delay
try:
    I2C_ADDRESS = int(args.I2C_Address, 16)  # Convert hex string to int
except ValueError:
    print(f"The I2C address {args.I2C_Address} is not a valid hex I2C address.")
    sys.exit(1)

ADC_BITS = 10
MAX_ADC_COUNT = pow(2, ADC_BITS) - 1

# Check if VREF is greater than 0
if args.vref <= 0:
    print("The reference voltage must be greater than 0.")
    sys.exit(1)

VREF = args.vref

bus = smbus.SMBus(1) # RPi revision 2 (0 for revision 1)

t = 0
print(f"I2C address {hex(I2C_ADDRESS)[:2] + hex(I2C_ADDRESS)[2:].upper()}, Vref {VREF}V")
print("Time\tADC\tVoltage")
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
    print(f"{t:3.1f}\t{data}\t{data*VREF/MAX_ADC_COUNT:.2f}V")

    t += SLEEP_TIME
    time.sleep(SLEEP_TIME)