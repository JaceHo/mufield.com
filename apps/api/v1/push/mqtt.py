# coding=utf-8
"""
Send metrics to an MQTT broker.

### Dependencies

* [client](http://client.org/documentation/python/)
* Python `ssl` module (and Python >= 2.7)

In order for this to do something useful, you'll need an
MQTT broker (e.g. [client](http://client.org) and
a `.conf` containing something along these lines:

        [server]
        handlers = .handler.mqtt.MQTTHandler
        ...
        [handlers]

        [[MQTTHandler]]
        host = address-of-mqtt-broker  (default: localhost)
        port = 1883         (default: 1883; with tls, default: 8883)
        qos = 0             (default: 0)
        tls = True          (default: False)
        cafile =        /path/to/ca/cert.pem
        certfile =      /path/to/certificate.pem
        keyfile =       /path/to/key.pem

        # Optional topic-prefix to prepend to metrics en-route to
        # MQTT broker
        prefix = some/pre/fix       (default: "")

        # If you want to connect to your MQTT broker with TLS, you'll have
        # to set the following four parameters
        tls = True          (default: False)
        cafile =        /path/to/ca/cert.pem
        certfile =      /path/to/certificate.pem
        keyfile =       /path/to/key.pem

Test by launching an MQTT subscribe, e.g.:

        client_sub  -v -t 'servers/#'

or
        client_sub -v -t 'some/pre/fix/#'

### To Graphite

You may be interested in
[mqtt2graphite](https://github.com/jpmens/mqtt2graphite)
which subscribes to an MQTT broker and sends metrics off to Graphite.

### Notes

* This handler sets a last will and testament, so that the broker
  publishes its death at a topic called clients//<hostname>
* Support for reconnecting to a broker is implemented and ought to
  work.

"""
import logging
import threading

from musicfield import settings
import paho.mqtt.client as mqtt

HAVE_SSL = True
try:
    import ssl
except ImportError:
    HAVE_SSL = False


class Metric(object):
    def __init__(self, topic, payload):
        self.topic = topic
        self.payload = payload


class MQTTHandler(object):
    """
    """

    def __init__(self):
        """
        Create a new instance of the MQTTHandler class
        """

        # Initialize Data
        self.mqttc = None
        # Initialize Lock
        self.lock = threading.Lock()
        self.client_id = settings.SECRET_KEY

        # Initialize Options
        self.retain = settings.MOSQUITTO_CONFIGS.get('retain', True)
        self.host = settings.MOSQUITTO_CONFIGS.get('host', 'localhost')
        self.qos = int(settings.MOSQUITTO_CONFIGS.get('qos', 2))
        self.tls = settings.MOSQUITTO_CONFIGS.get('tls', False)

        # Initialize
        self.mqttc = mqtt.Client(self.client_id, clean_session=False)

        self.auth = {'username': settings.MOSQUITTO_CONFIGS.get('username', 'admin'),
                     'password': settings.MOSQUITTO_CONFIGS.get('password', 'mfadmin')}

        if not self.tls:
            self.port = int(settings.MOSQUITTO_CONFIGS.get('port', 1883))
        else:
            # Set up TLS if requested
            self.port = int(settings.MOSQUITTO_CONFIGS.get('port', 8883))
            self.cafile = settings.MOSQUITTO_CONFIGS.get('cafile', None)
            self.certfile = settings.MOSQUITTO_CONFIGS.get('certfile', None)
            self.keyfile = settings.MOSQUITTO_CONFIGS.get('keyfile', None)

            if None in [self.cafile, self.certfile, self.keyfile]:
                logging.error("MQTTHandler: TLS configuration missing.")
                return

        try:
            self.mqttc.tls_set(
                self.cafile,
                certfile=self.certfile,
                keyfile=self.keyfile,
                cert_reqs=ssl.CERT_REQUIRED,
                tls_version=3,
                ciphers=None)
        except:
            logging.error("MQTTHandler: Cannot set up TLS "
                          + "configuration. Files missing?")

        self.mqttc.connect(self.host, self.port, 60)


    def publish(self, metrics, qos=None, retain=None):
        if isinstance(metrics, Metric):
            metrics = [metrics]

        for metric in metrics:
            self.mqttc.publish(metric.topic, metric.payload, self.qos if not qos else self.qos,
                               self.retain if not retain else self.retain)


