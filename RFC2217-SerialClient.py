#!/usr/bin/env python3

import sys

import serial


def main(argv):
    with serial.serial_for_url('rfc2217://192.168.57.250:4098', baudrate=4800, timeout=2) as ser:
        while(1):
            read = ser.readline().strip()
            print(read)

'''
[program:IOGrabber]
command= python3 RFC2217-SerialClient.py
user=base
'''

if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt:

        print('Received Ctrl-c')
