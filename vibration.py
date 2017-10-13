import time
import logging
import sys
from exception import ServiceExit
from soceadapter import SoCEAdapter


class bbuVibration(SoCEAdapter):

    def __init__(self,name):
        super(bbuVibration, self).__init__(name)
     
    def run(self):
        while True:
            try:
                readings = self.getReadings()
                if readings:
                    for key, value in readings.iteritems():
                        logging.debug("Key: %s & value: %s", key, value)
                time.sleep(0.5)
            except ServiceExit:
                self.cleanUp()
                break

if __name__ == '__main__':
    k = bbuVibration(sys.argv[1])
    k.run()
