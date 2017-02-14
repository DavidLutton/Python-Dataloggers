#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import serial
#import datetime
import time
import pika


time.sleep(30) # sleep 30 seconds when starting # make safe at boot time
'''
   ./serial/by-path/pci-0000:00:14.0-usb-0:3:1.0-port1 -> ../../ttyUSB1
   ./serial/by-path/pci-0000:00:14.0-usb-0:3:1.0-port0 -> ../../ttyUSB0
   ./serial/by-id/pci-Inside_Out_Networks_Edgeport_2_V34014802-0-if00-port1 -> ../../ttyUSB1
   ./serial/by-id/pci-Inside_Out_Networks_Edgeport_2_V34014802-0-if00-port0 -> ../../ttyUSB0
'''

def nanostr(timenow):
    l = list( "{0:.9f}".format( timenow ) )  # convert to list
    p = l.index(".")  # find position of the letter "a"
    del(l[p])         # delete it
    return ( "".join(l) )  # convert

def main(argv):

    ser = serial.Serial('/dev/ttyUSB0', 4800, timeout=1)

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='GPS')

    inittime = time.strftime("%Y%m%d-%H%M%S")

#    with open("/home/rn/Desktop/GPS/GPS-"+inittime+".log","a") as logfile:
    while(1):

        read = ser.readline()
        timestamp = int(nanostr( time.time() ))

        if read.startswith(b'$') == True:
            readme = bytes.decode(read)
            #print(read)
            print(readme.strip())
            #logfile.write(readme)
            #print(dir(logfile))
            #logfile.flush()
            channel.basic_publish(
                exchange='',
                routing_key='GPS',
                body=readme,
                properties=pika.BasicProperties(
                    expiration=str(6000000),
                    timestamp=timestamp,
                        #headers=headers
                    )
                )


'''
ser.close()
connection.close()
'''

'''
[program:GPSIOGrabber]
command= python3 /home/rn/Desktop/GPS_State_Logger/IO_GPS_RX.py
user=rn
'''

if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt:

        print('Received Ctrl-c')
