from adapterconfig import AdapterConfig
import json
import logging
import time
import paho.mqtt.client as paho
import cpppo
import ssl
from exception import ServiceExit
from types import DictType, StringType
from alerthandler import alerthandler
from pymodbus.client.sync import ModbusTcpClient as ModbusClient

class ModBusAdapter(AdapterConfig):
    """ 
    Handles reading holding registers from a Modbus device
    """  

    def __init__(self, name):
        super(ModBusAdapter, self).__init__(name)


        self.client = paho.Client()
        self.alertHandler = alerthandler()


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

    def telemetryCloud(self, id, value):
        #lookup id

        def tel():
            pass
       
    
        tag = self.tag
        tel.name = tag
        tel.value = value
        return str([json.dumps(tel.__dict__)]).replace("'","")
    
    def __db_error(self, connection, cursor, errorclass, errorvalue):
         logging.info("CE Connection Error (class): %s : (value): %s", errorclass, errorvalue) 
        
    def publishSB(self, msg):
        """ Publishes the readings to an mqtt broker:

        :param :msg: Formatted message appropriate for the subscriber
        """
          
        logging.debug(msg)
       
        if not all(chr in msg for chr in 'state'):
            self.client.publish(self.topic,
                payload=msg, qos=0, retain=False)
        else:             
            self.client.publish(self.alertTopic,
                payload=msg, qos=0, retain=False)

    def getReadings(self):

        ret = {}
        try:
            with ModbusClient(self.host, port=self.port) as client:
                result = client.read_holding_registers(self.register, self.length, unit=self.unit)
                if result.registers:
                    ret[self.tag] = result.registers[0]  #assumes length of 1

            if ret:
                return ret

            return None

        except Exception as e:
            logging.info(e.message)
            return None
            