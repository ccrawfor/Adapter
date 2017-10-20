from __future__ import division
import time
import logging
import sys
from exception import ServiceExit
from modbusadapter import ModBusAdapter


class bbuTemperature(ModBusAdapter):

    def __init__(self,name):
        super(bbuTemperature, self).__init__(name)
     
    def run(self):
        while True:
            try:
                readings = self.getReadings()
                if readings:
                    for key, value in readings.iteritems():
                        logging.debug("Key: %s & value: %s", key, value)
                        temp = value / 10 
                        self.publishSB(self.telemetryCloud(key, temp))
                time.sleep(1.0)
            except ServiceExit:
                self.cleanUp()
                break

if __name__ == '__main__':
    k = bbuTemperature(sys.argv[1])
    k.run()
