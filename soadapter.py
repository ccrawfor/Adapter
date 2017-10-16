
import pymssql
import adodbapi
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

class SoAdapter(AdapterConfig):
    """ 
    Handles reading data from a SQL Express or SQL Compact Edition database.
    """    

    def __init__(self, name):
        super(SoAdapter, self).__init__(name)


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
            
        tag = id
        tel.name = tag
        tel.value = value
        return str([json.dumps(tel.__dict__)]).replace("'","")
    
    def __db_error(self, connection, cursor, errorclass, errorvalue):
         logging.info("CE Connection Error (class): %s : (value): %s", errorclass, errorvalue) 
        
    def publishSB(self, msg, topic):
        """ Publishes the readings to an mqtt broker:

        :param :msg: Formatted message appropriate for the subscriber
        """
        
        tpc = "/devices/%s/measurements" % topic
        logging.debug(tpc)
        if not all(chr in msg for chr in 'state'):
            self.client.publish(tpc,
                payload=msg, qos=0, retain=False)
        else:             
            self.client.publish(self.alertTopic,
                payload=msg, qos=0, retain=False)

    def getReadings(self):

        if self.type == 'sqlexpress':
           conn = pymssql.connect(server=self.svr, user=self.usr, password=self.pwd, database=self.db, port=self.prt, host=self.hst)
        elif self.type == 'compact':
             conn_args = {'database': self.db}
             conn_args['connection_string'] = """Provider=Microsoft.SQLSERVER.CE.OLEDB.4.0;Data Source=%(database)s;"""
             conn = adodbapi.connect(conn_args)
             conn.connector.CursorLocation = 2
             conn.errorhandler = self.__db_error
             logging.debug("Connection Open")
            
        ret = {}
        
        
        for key, value in self.sql.items():
            if type(value) is dict:
                for k, v in value.items():
                    if not type(v) is list:
                        cur = conn.cursor()
                        cur.execute(v)
                        for row in cur.fetchall():
                            if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
                                self.dumpRecords(row, v, value.get('position'), key)
                            ret[key] = [row[(value.get('position'))[0]],value.get('topic')[0]]
                        cur.close()
        
        conn.close()
        logging.debug("Connection Closed")
        if ret:
            return ret

        return None

    def dumpRecords(self, row, sql, pos, key):
        values = []
        cnt = 0
        for x in pos:
            cnt = cnt + 1
            values.append(row[x])
            if cnt > 5:
                break

		
        logging.debug(key + " : " + sql + " : " + str(values))
      