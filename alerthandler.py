import logging

class alerthandler(object):
    #alerts = defaultdict(list)
    alerts = {}
    def __init__(self):
        pass
    def recordAlert(self, key, value):
        try:
            k = self.alerts[key]
            #bisect maybe more efficient
            if not value in self.alerts[key]:
                self.alerts.get(key).append(value)

        except KeyError:
            #key doesn't exist lets add it
            l = list()
            l.append(value)
            self.alerts[key] = l

    def dumpAlerts(self):
        #troubleshooting
        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
            for key, value in self.alerts.iteritems():
                logging.debug("Dumping Existing Alerts:")
                logging.debug("Alert Key: %s" % key)
                logging.debug("Alert Value: %s" % value)

    def clearAlerts(self, key):
        try:
            k = self.alerts[key]
            return iter(k)
        except KeyError:
            return iter([])

    def alertExists(self, key, value):
        try:
            #bisect maybe more efficient
            if not value in self.alerts[key]:
                return False
            else:
                return True
        except KeyError:
            #key doesn't exist lets add it
            return False

    def resetAlerts(self, key):
        #should reset based on clear return code
        self.alerts.pop(key, None)
        #del self.alerts[key]