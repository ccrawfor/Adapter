# pylint: disable-msg=E1101
import logging
from logging.handlers import RotatingFileHandler
import signal
from config import settings
from exception import ServiceExit

class AdapterConfig(object):
        """ Adapter initialization.
            This class processes the config.yaml        
        """    

        def __init__(self, name):
            """ Adapter initialization.
            :param name: The name of the device as defined in the configuration file.
            """
            logging.getLogger().setLevel(logging.DEBUG)
            logging.getLogger("enip").setLevel(logging.WARNING)
            logging.getLogger("cpppo").setLevel(logging.WARNING)
            signal.signal(signal.SIGTERM, self.service_shutdown)
            signal.signal(signal.SIGINT, self.service_shutdown)
            rfh = RotatingFileHandler(settings['relayr']['logpath'] + name + '.log', mode='a', maxBytes=10485760, backupCount=5, encoding=None, delay=0)
            rfh.setLevel(settings['relayr']['loglevel'])
            frm = logging.Formatter('[%(asctime)s - %(filename)s:%(lineno)s - %(funcName)s ] %(message)s')
            rfh.setFormatter(frm) 
            logging.getLogger().addHandler(rfh)
            
            self.mqttRC = {0:"Connection Successful", 1:"Connection refused - Incorrect protocol version",
            2:"Connection refused - Invalid Client Identifier", 3:"Connection refused - Server unavailable",
            4:"Connection refused - bad username or password",5:"Connection refused - not authorized" }
            
            #mqtt client settings
            #what type of device are we
            self.init = None
            self.type = None
            dev = settings['devices']
            vendors = settings['vendors']
            if 'plc' in dev and dev['plc']:
                if 'enip' in dev['plc']:
                    if (dev['plc']['enip']):
                        if (name in dev['plc']['enip']):
                                self.init = dev['plc']['enip'][name]
                                self.host = self.init.get('host')	# Controller IP address
                                self.port = self.init.get('port')	# default is port 44818
                                self.depth = self.init.get('depth')		# Allow 1 transaction in-flight
                                self.multiple = self.init.get('multiple')		# Don't use Multiple Service Packet
                                self.fragment = self.init.get('fragment')		# Don't force Read/Write Tag Fragmented
                                self.timeout	= self.init.get('timeout')		# Any PLC I/O fails if it takes > 1s
                                self.printing = self.init.get('printing')		# Print a summary of I/O
                                self.tags = self.init.get('tags')
                                assert self.tags, 'Tag list cannot be empty'
                                self.endPoint = settings['protocol']['type'] + ":" + settings['protocol']['path']
                                self.topic = self.init.get('topic')
                                self.alertTopic = self.init.get('alertTopic')
                                self.type = 'enip'
                                self.mqPword = self.init.get('mqPword', None)
                                self.mqDevice = self.init.get('mqDevice', None)
                                #add self assert to check for existence of both.
                                if (self.mqPword is None) or (self.mqDevice is None):
                                    assert False, 'Device missing device and password'
                else:
                    if ('modbus' in dev['plc']):
                        if (dev['plc']['modbus']):
                            if (name in dev['plc']['modbus']):
                                self.init = dev['plc']['modbus'][name]
            #expand to include known sensors
            if not (self.init):
                logging.debug('Device not found Checking Vendors')
            if  settings['relayr']['mqtt_credentials']:
                self.mqUser = settings['relayr']['mqtt_credentials']['user']         
                self.mqPwd = settings['relayr']['mqtt_credentials']['password']
            self.mqServer = settings['relayr']['mqtt_server']
            #self.mqServer = settings['relayr']['mqtt_server']['server']
            self.mqHost = self.mqServer.get('server')
            self.mqPort = self.mqServer.get('port')
            self.mqKeepAlive = self.mqServer.get('keepalive')
            #if using ifm smart observer
            if 'ifm' in vendors and vendors['ifm']['smartobserver']:
                if (name in vendors['ifm']['smartobserver']):
                    self.init = vendors['ifm']['smartobserver']['sqlexpress']
                    self.svr = self.init.get('server')
                    self.usr = self.init.get('user')
                    self.pwd = self.init.get('password')
                    self.prt = self.init.get('port')
                    self.hst = self.init.get('host')
                    self.db = self.init.get('database')
                    self.sql = self.init.get('sql')
                    self.mqPword = self.init.get('mqPword', None)
                    self.mqDevice = self.init.get('mqDevice', None)
            
            print self.svr
            if not (self.svr):
                
                assert False, 'server not found' 


        def cleanUp(self):
            if (self.client):
                self.client.disconnect()

        def service_shutdown(self, signum, frame):
            logging.info('Caught signal %d' % signum)            
            raise ServiceExit                          
