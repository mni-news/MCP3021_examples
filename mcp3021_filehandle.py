# This program is an exmaple of reading the MCP3021 ADC using a file handle.
# The program reads the ADC value and converts it to voltage
# The first byte contains the 4 most significant bits of the ADC value and
# the second byte contains the 6 least significant bits of the ADC value
# as the 6 most significant bits of that byte.)
#
#        0 0 0 0 D9 D8 D7 D6     D5 D4 D3 D2 D1 D0 0 0
#
# The I2C address is on bus 1 (from i2cdetect -y 1)

import io
import sys
import fcntl
import time
import argparse

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
I2C_SLAVE_COMMAND = 0x0703
I2C_DEVICE_PATH = "/dev/i2c-1"

# Check if VREF is greater than 0
if args.vref <= 0:
    print("The reference voltage must be greater than 0.")
    sys.exit(1)

VREF = args.vref

# set device address
FileHandle = io.open(I2C_DEVICE_PATH, "rb", buffering=0)
fcntl.ioctl(FileHandle, I2C_SLAVE_COMMAND, I2C_ADDRESS)

if __name__ == "__main__":
    t = 0
    print(f"I2C address {hex(I2C_ADDRESS)[:2] + hex(I2C_ADDRESS)[2:].upper()}, Vref {VREF}V")
    print("Time\tADC\tVoltage")
    while True:
        try:
            value = list(FileHandle.read(2))
        except OSError as e:
            print(f"There is no I2C device present at {hex(I2C_ADDRESS)[:2] + hex(I2C_ADDRESS)[2:].upper()}.")
            sys.exit(1)
        # Swap bytes and remove the 2 least significant bits.
        data = (value[0] * 256 + value[1]) >> 2
        print(f"{t:3.1f}\t{data}\t{data*VREF/MAX_ADC_COUNT:.2f}V")
        t += SLEEP_TIME
        time.sleep(SLEEP_TIME)

