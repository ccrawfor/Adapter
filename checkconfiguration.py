from config import settings
from types import DictType, StringType
import json
import sys
import collections



def checkConfiguration(name, tag):

    init = None
    dev = settings['devices']
    vendors = settings['vendors']
    if 'plc' in dev and dev['plc']:
        if 'enip' in dev['plc']:
            if (dev['plc']['enip']):
                if (name in dev['plc']['enip']):
                        init = dev['plc']['enip'][name]
                        print init.get(tag, "None")
    if ('modbus' in dev['plc']):
                        if (dev['plc']['modbus']):
                            if (name in dev['plc']['modbus']):
                                init = dev['plc']['modbus'][name]                
                                print init.get(tag, "None")

    if name == 'sqlexpress':
        if 'ifm' in vendors and vendors['ifm']['smartobserver']:
            if (name in vendors['ifm']['smartobserver']):
                init = vendors['ifm']['smartobserver'][name]
                print init.get(tag, "None")
    elif name == 'compact': #compact edition
        init = vendors['ifm']['smartobserver']['compact']                    
        print init.get(tag, "None")    

    

def testPLCTags(name, tag, value):
    init = None
    dev = settings['devices']
    if 'plc' in dev and dev['plc']:
        if 'enip' in dev['plc']:
            if (dev['plc']['enip']):
                if (name in dev['plc']['enip']):
                        init = dev['plc']['enip'][name]['tags']
                        v = init[tag][str(value)]
                        print ("%s : %s : %s" % (name, tag, v))
                        print ("")
                        print ("Printing tag & description:")
                        for x in v:
                            print x

def dumpSettings(name):
    dev = settings['devices']
    vendors = settings['vendors']
    if 'plc' in dev and dev['plc']:
        if 'enip' in dev['plc']:
            if (dev['plc']['enip']):
                if (name in dev['plc']['enip']):
                        init = dev['plc']['enip'][name]
                        k = collections.OrderedDict(init)
                        for key, value in k.iteritems():
                            print ("%s : %s" %(key, value))
    if ('modbus' in dev['plc']):
                        if (dev['plc']['modbus']):
                            if (name in dev['plc']['modbus']):
                                init = dev['plc']['modbus'][name]
                                k = collections.OrderedDict(init)                
                                for key, value in k.iteritems():
                                    print ("%s : %s" %(key, value))

    if name == 'sqlexpress':
        if 'ifm' in vendors and vendors['ifm']['smartobserver']:
            if (name in vendors['ifm']['smartobserver']):
                init = vendors['ifm']['smartobserver'][name]
                k = collections.OrderedDict(init)
                for key, value in k.iteritems():
                    print ("%s : %s" %(key, value))
    elif name == 'compact': #compact edition
        init = vendors['ifm']['smartobserver']['compact']
        k = collections.OrderedDict(init)                    
        for key, value in k.iteritems():
             print ("%s : %s" %(key, value))  
                           

if __name__ == '__main__':

    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print ("Usage: <target> [<name> <key> | <name> <key> <value>]")
        print ("<target> matches to device name (plc, modbus, smart observer) specified in the config.yaml")
    
    print ("")
    print ("")

    if len(sys.argv) == 2:
        print ("+++++++++++++++++++++++Dumping Settings Begin++++++++++++++++++++")
        print ("")
        dumpSettings(sys.argv[1])
        print ("+++++++++++++++++++++++Dumping Settings End++++++++++++++++++++")
        print ("")
    if len(sys.argv) == 3:
        print ("+++++++++++++++++++++++Check Key Begin++++++++++++++++++++")
        print ("")
        checkConfiguration(sys.argv[1], sys.argv[2])
        print ("+++++++++++++++++++++++Check Key End++++++++++++++++++++")
        print ("")
    if len(sys.argv) == 4:
        print ("+++++++++++++++++++++++Check Alert Begin++++++++++++++++++++")
        print ("")
        testPLCTags(sys.argv[1], sys.argv[2], sys.argv[3])
        print ("+++++++++++++++++++++++Check Alert End++++++++++++++++++++")
        print ("")
        