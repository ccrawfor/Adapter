import time
import logging
import sys
from exception import ServiceExit
from adapter import Adapter

class bbuAdapter(Adapter):

    def __init__(self,name):
        super(bbuAdapter, self).__init__(name)
     
    def run(self):
        while True:
            try:
                readings = self.getReadings()
                if readings:
                    for key, value in readings.iteritems():
                        logging.debug("Key: %s & value: %s", key, value)
                        #self.publishSB(self.telemetry(key, value))
                        if not self.isAlert(key):
                            self.publishSB(self.telemetryCloud(key, value))
                        else:
                            self.sendAlert(key, value)
                time.sleep(0.5)
            except ServiceExit:
                self.cleanUp()
                break

if __name__ == '__main__':
    k = bbuAdapter(sys.argv[1])
    k.run()