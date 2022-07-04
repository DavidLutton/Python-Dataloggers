
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import serial
import time
# import requests
import pynmea2

from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# You can generate a Token from the "Tokens Tab" in the UI
token = "TOKEN"
org = "ORG"
bucket = "BUCKET"

client = InfluxDBClient(url="http://127.0.0.1:8086", token=token)


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
    write_api = client.write_api(write_options=SYNCHRONOUS)

    data = f"{datum} value={value}"
    # print(data)
    write_api.write(bucket, org, data)

def main(argv):
    while(True):
        read = b'...'
        while(read != b''):
            time.sleep(5)
            try:
                with serial.Serial('/dev/ttyS1', 4800, timeout=2) as ser:
                    while(read != b''):
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


if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt:

        print('Received Ctrl-c')
