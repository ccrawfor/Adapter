# pylint: disable-msg=E1101
import json
import logging
import time
import paho.mqtt.client as paho
import cpppo
import ssl
from cpppo.server.enip import address, client
from exception import ServiceExit
from adapterconfig import AdapterConfig
from types import DictType, StringType

class Adapter(AdapterConfig):
        """ Adapter handles the reading and publishing of data. 
            
            Configuration data can be handled in the subclass by importing

            from config import settings

            Key/Values in the configuration file match those used to configure.
            as an example:

            devices:

                plc:

                    enip:

                        plc1:

                            host: somehost

                            port: 1883

            settings['devices']['plc']['enip']['plc1']['host']  

        """    
        def __init__(self, name):
            super(Adapter, self).__init__(name)
            """
            self.clientAlert = paho.Client()
            self.clientAlert.username_pw_set(self.mqUser, self.mqPwd)
            self.clientAlert.on_connect = self.__on_alert_connect
            self.clientAlert.on_publish = self.__on_alert_publish
            self.clientAlert.tls_set('/etc/ssl/certs/ca-certificates.crt', certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED,
    tls_version=ssl.PROTOCOL_TLSv1, ciphers=None)
            self.clientAlert.tls_insecure_set(True)
            self.clientAlert.connect(self.mqServer, self.mqPort, self.mqKeepAlive)
            self.clientAlert.loop_start()            
            """
            self.client = paho.Client()
        
            if not (self.mqDevice) is None:
                logging.debug("Using Device Credentials")
                self.client.username_pw_set(self.mqDevice, self.mqPword)
            else:
                self.client.username_pw_set(self.mqUser, self.mqPwd)
            
            self.client.on_connect = self.__on_connect
            self.client.on_publish = self.__on_publish
            if not (self.mqServer.get('ca_cert', None)) is None:
                self.client.tls_set(self.mqServer.get('ca_cert_pem'), certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1, ciphers=None)                
                self.client.tls_insecure_set(False)
        
            self.client.connect(self.mqHost, self.mqPort, self.mqKeepAlive)
            self.client.loop_start()

        def __on_connect(self, client, userdata, flags, rc):
            """ Callback triggered when connected to the MQTT broker.
            :param client: the client instance for this callback
            :param userdata: the private user data as set in Client() or userdata_set()
            :param flags: response flags sent by the broker
            :param rc: the connection result

                0: Connection successful 
                
                1: Connection refused - incorrect protocol version 
                
                2: Connection refused - invalid client identifier 
                
                3: Connection refused - server unavailable 
                
                4: Connection refused - bad username or password 
                
                5: Connection refused - not authorised 6-255: Currently unused.
                
            :return: None
            """
            
            logging.info("Connected to the MQTT broker: %s with Client: %s", self.mqttRC.get(rc, "None"), client)

        def __on_alert_connect(self, client, userdata, flags, rc):
            logging.info("Connected to the MQTT broker for alerts: %s with Client: %s",  self.mqttRC.get(rc, "None"), client)

        def __on_publish(self, client, userdata, mid):
            logging.debug("MESSAGE SENT: %s : Using Client: %s", mid, client)

        def __on_alert_publish(self, client, userdata, mid):
            logging.debug("MESSAGE SENT: %s : Using Alert Client: %s", mid, client)    

        def timestamp(self):
            """ Returns the time in milliseconds.
            Uses the systems current time.      
            :return: Time in milliseconds
            """
            d_s = time.time()
            d_in_ms = int(d_s)*1000
            return d_in_ms

        def telemetry(self, id, value):
            """ Agent formatted message {"id":<id>, "ts":<timestamp>, "value":<value>}

            :param :id: API Name

            :param :value: device reading

            :return: Formatted message
            """    
            def tel():
                pass
            tel.id = id
            tel.ts = self.timestamp()
            tel.value = value
            return json.dumps(tel.__dict__)
        
        def telemetryCloud(self, id, value):
            #lookup id
            try:
                def tel():
                    pass
                def alert():
                    pass    
                if type(self.tags.get(id)) is StringType:    
                    tag = self.tags.get(id)
                    tel.name = tag
                    tel.value = value
                    return str([json.dumps(tel.__dict__)]).replace("'","")
                elif type(self.tags.get(id)) is DictType:
                    #Needs review / logic to reset / clear the alert.
                    alert.name = self.tags[id][str(value)][0]
                    alert.message = self.tags[id][str(value)][1]
                    alert.state = "set"
                    return str([json.dumps(alert.__dict__)]).replace("'","")
            except KeyError:
                logging.info("Tag does not exist: %s" % id)
                raise ServiceExit


        def legacyMsg(self):
            """ Hack for quick tests
            :return: formatted message
            """      
            def leg():
                pass
            leg.meaning = "Registry"
            leg.value = "True"
            return json.dumps(leg.__dict__)
           

    

        def publishSB(self, msg):
            """ Publishes the readings to an mqtt broker:

            :param :msg: Formatted message appropriate for the subscriber
            """
            logging.debug(msg)
            #logger.debug(msg)
            if not all(chr in msg for chr in 'state'):
                self.client.publish(self.topic,
                    payload=msg, qos=0, retain=False)
            else: 
                logging.info("+++++++++Alert+++++++++++")             
                self.client.publish(self.alertTopic,
                   payload=msg, qos=0, retain=False)

        def getReadings(self):
            """ Pivots off of the known and supported device types or protocols. For instance:
            PLC -> <ENIP> : PLC -> <MODBUS> or Sensors -> IFM -> PIR etc.  Can be overridden for new 
            device types and rolled up during a QA process.  
            :param :None:

            :return: Devices readings or None.

            For ENIP protocol it returns a dictionary of the tags and values
            """
            if self.type == 'enip':
                 ret = {}
                 with client.connector( host=self.host, port=self.port, timeout=self.timeout ) as connection:
                        operations = client.parse_operations( self.tags )
                        failures,transactions = connection.process(
                            operations=operations, depth=self.depth, multiple=self.multiple,
                              fragment=self.fragment, timeout=self.timeout )
                            #fire and forget
                        for idx, val in enumerate(self.tags):
                            if isinstance(transactions[idx], list):
                                 ret[val]=transactions[idx][0]
                 if ret:
                    return ret       

            return None
            

