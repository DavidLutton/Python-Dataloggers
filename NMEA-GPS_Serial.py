#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import serial
import time
import requests
import pynmea2


def GPS_RMC(msg):
    if msg.status == "A":
        send("RMCFix", "1")
    else:
        send("RMCFix", "0")


def GPS_GSA(msg):
    # print(repr(msg))
    # print(dir(msg))
    send('GSA3d', msg.mode_fix_type)


def GPS_GSV(msg):
    # print(repr(msg))
    send('GSView', msg.num_sv_in_view)


def GPS_GGA(msg):
    # print(repr(msg))
    send('GGA', msg.num_sats)

    
dispatch = {
    'GGA' : GPS_GGA,
    # b'$PRWIZC' : do_sink,
    'GSA' : GPS_GSA,
    'GSV' : GPS_GSV,
    'RMC' : GPS_RMC,
}


def send(datum, value):
    payload = "{0!s} value={1!s}".format(datum, value)
    try:
        r = requests.post("http://192.168.57.103:8086/write?db=GPSRadio0", data=payload)
    except requests.exceptions.ConnectionError:
        print("Failed to Connect to InfluxDB")


def main(argv):
    while(True):
        read = b'...'
        while(read is not b''):
            time.sleep(5)
            try:
                with serial.serial_for_url('rfc2217://192.168.57.250:4098', baudrate=4800, timeout=2) as ser:
                    while(read is not b''):
                        read = ser.readline().strip()
                        # print(read)
                        if read.startswith(b'$') and not read.startswith(b'$PRWIZCH'):
                            try:
                                msg = pynmea2.parse(read.decode())
                            except UnicodeDecodeError:
                                pass
                            # print(dir(msg))
                            # print(msg.sentence_type)
                            try:
                                dispatch[msg.sentence_type](msg)
                            except KeyError:
                                pass
                            except pynmea2.nmea.ChecksumError:
                                print("Checksum Error")
            except serial.serialutil.SerialException:
                print("Connection Failed")


'''
[program:GPS_Serial]
command= python3 NMEA-GPS_Serial.py
user=base
'''

if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt:

        print('Received Ctrl-c')
