#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys


import pika
import subprocess

import yaml

import pycurl
from urllib.parse import urlencode
from pprint import pprint


def do_sink( arg, timestr ):
    #return '\n'.join(os.listdir(arg))
    print ( arg )
    #return ( arg )

def GPS_GPRMC( arg, timestr ):
    RMCFix = arg[14:15].decode()
    if RMCFix == "A":
        RMCFix = "1"
    elif RMCFix == "V":
        RMCFix = "0"
    else:
        RMCFix = "-1"

    print (RMCFix)
    compose = ['curl', '-i', '-XPOST', 'http://localhost:8086/write?db=CALGPS', '--data-binary', 'RMCFix value='+RMCFix+" "+ timestr ]
    #pprint(compose)
    subprocess.call(compose)
    #return ( arg )

def GPS_GPGSA( arg, timestr ):
    data = arg.decode()
    split = data.split(",")
    #print (split[2])
    #print (split)
    compose = ['curl', '-i', '-XPOST', 'http://localhost:8086/write?db=CALGPS', '--data-binary', 'GSA3d value='+split[2]+" "+ timestr ]
    subprocess.call(compose)
    #print(split[3:15])
    sats = 0
    for sat in split[3:15]:
        if sat != '':
            sats = sats + 1
    #print(sats)
    compose = ['curl', '-i', '-XPOST', 'http://localhost:8086/write?db=CALGPS', '--data-binary', 'GSASats value='+str(sats)+" "+ timestr ]
    subprocess.call(compose)


def GPS_GPGGA( arg, timestr ):
    data = arg.decode()
    split = data.split(",")
    #pprint (split)
    #pprint (split[7])
    compose = ['curl', '-i', '-XPOST', 'http://localhost:8086/write?db=CALGPS', '--data-binary', 'GGA value='+split[7]+" "+ timestr ]
    subprocess.call(compose)


def GPS_GPGSV( arg, timestr ):
    data = arg.decode()
    split = data.split(",")
    #print (split)
    #print (split[3])
    compose = ['curl', '-i', '-XPOST', 'http://localhost:8086/write?db=CALGPS', '--data-binary', 'GSView value='+split[3]+" "+ timestr ]
    subprocess.call(compose)



dispatch = {
    b'$GPGGA,' : GPS_GPGGA,
    b'$PRWIZC' : do_sink,
    b'$GPGSA,' : GPS_GPGSA,
    b'$GPGSV,' : GPS_GPGSV,
    b'$GPRMC,' : GPS_GPRMC,
}

def callback(ch, method, properties, body):
    #pprint(body[0:7])

    dispatch[ body[0:7] ]( body, str(properties.timestamp ))
    #body = body.decode()

 #   pprint(con)
#    data = yaml.load(con)




def main(argv):

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='GPS')
    channel.basic_consume(callback, queue='GPS', no_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()





if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        print('Received Ctrl-c')
