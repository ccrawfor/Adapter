import time
import logging
import sys
from exception import ServiceExit
from soadapter import SoAdapter


class bbuVibration(SoAdapter):

    def __init__(self,name):
        super(bbuVibration, self).__init__(name)
     
    def run(self):
        while True:
            try:
                readings = self.getReadings()
                if readings:
                    for key, value in readings.iteritems():
                        logging.debug("Key: %s & value: %s", key, value)
                        self.publishSB(self.telemetryCloud(key, value[0]),value[1])
                time.sleep(30.0)
            except ServiceExit:
                self.cleanUp()
                break

if __name__ == '__main__':
    k = bbuVibration(sys.argv[1])
    k.run()
