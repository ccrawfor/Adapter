# Generic Adapter Framework (Python)


## Description

A generic adapter framework for Python initially targeting Python 2.7.x.



## Overview

The intent of the framework is to provide internal as well as external (System Integrator) support for bridging devices.

This should allow one the ability to focus on creating reference architectures and or MVPs without having to necessarily understand the details of interfacing with the agent itself.

| Supported Devices | Protocol | Comments |
|:------------|:---------------|:------------------|
| Allen Bradley 1769-L33ER PLC | EtherNet/IP CIP | Leverages the [CPPPO](https://github.com/pjkundert/cpppo) libraries

## Dependencies

pip install pyyaml

pip install paho-mqtt

Device specific dependencies (EtherNet/IP CIP)

* pip install cpppo

## Modules

<u>**adapterconfig**</u> Performs adapter initialization.

* *class* **adapterconfig.AdapterConfig** 

**AdapterConfig** provides two public methods.

* *adapterconfig.service_shutdown* Convenience method that handles python signals and raises a custom exception class (ServiceExit).

* *adapterconfig.cleanup* Convenience method for handling object cleanup.  

<u>**config**</u> Convenience module for reading the configuration file and converting it to a Python object.

* **settings** instance attribute containing the converted configuration file.

<u>**exception**</u> Convenience module for defining custom exception classes.

* *class* **exception.ServiceExit** 

**adapter** Handles the reading and publishing of data.

* *class* **adapter.Adapter**  

<u>**Adapter**</u> contains two private methods specific to handling MQTT callbacks as well as five public methods.  This class should contain all the data that can be reported by the agent:

* telemetry
* alerts
* events
* configuration
* topology (peers)
* metadata



* *Adapter.__on_connect* callback method to handle the brokers response to our connection request.

* *Adapter.__on_publish* not currently used.

* *Adapter.timestamp* convenience method for returning the time in milliseconds.

* *Adapter.telemetry(id, value)* convenience method for formatting the payload for time series telemetry data values.

```json
{
    "id": "temperature",    
    "ts": 1492515087123,    
    "value": 42.5           
}
```
* *Adapter.alert(id, value)* placeholder.  It is intended to be used as a convenience method for formatting payload for alerts.

* *Adapter.publishSB(msg)* publishes the formatted data.

* *Adapter.getReadings()* Pivots off of the known device types and returns the devices readings.


## Configuration
 
The **org** list contains entries for the mqtt broker.  If provided, the adapter will use the mqtt_credentials.  
 
```
org:
    mqtt_server:
        server : mqtt.org.io
        port : 1883
        keepalive : 60
    pub_freq_ms : 500
    loglevel : 20  # DEBUG=10,INFO=20,WARNING=30, etc
    mqtt_credentials:
        user : user
        password : password
        clientId : client
        topic : topic  #should contain closing forward slash /xxx/xx/
```

**Devices** list is broken down by the following

* *plc* (product line controllers)
	*  enip (protocol) 
		* name (device name)
			* device specific settings	

```
devices:
    plc:
        enip:
            plc1:
                host : localhost   # Controller IP address
                port : 44818   #default port
                depth : 1   # Allow 1 transaction in-flight
                multiple : 0   # Don't use Multiple Service Packet
                fragment : False   # Don't force Read/Write Tag Fragmented
                timeout : 1.0   # Any PLC I/O fails if it takes > 1s
                printing : False   # Print a summary of I/O
                tags : ["HZ", "Alarm", "Cycles"] # Probably need to take into account the data types.
                topic : /v1/0739c6ac-2a30-4aa2-b3ee-166ddd72264d/data

```

Additional consideration is given for various sensors broken down, if possible, by manufacturer.

```
devices:
	ifm:
	grove:
	zwave:
```

## Use

Ideally for each device / sensor you will create a derived class from **Adapter**. In it's constructor call the parent's initializer passing in the devices name.  If the device is currently supported then all you should have to do is call the *Adapter.getReadings()* method.  Otherwise, override the getReadings() method in the derived class.

Next, call the *Adapter.publishSB(msg)* with the data supported by the agent.  *Adapter.telemetry(id,value)*.

```
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
                        self.publishSB(self.telemetry(key, value))
                time.sleep(0.02)
            except ServiceExit:
                self.cleanUp()
                break

if __name__ == '__main__':
    k = bbuAdapter(sys.argv[1])
    k.run()

``` 
 
 
## To-Do

* Replace loading of configuration file from current directory to an Environment Variable.  This allows us to minimally secure the configuration file to the root / service account running the adapter.

* Replace MQTT broker connection status with meaningful message.

* Consider additional refactoring for abstracting the creation of devices behind a factory method pattern.

* Revise configuration file to move host under middleware which will allow us to publish to multiple platforms such as AWS, Google, Oracle with each device specifying where they want the data published to.


 

