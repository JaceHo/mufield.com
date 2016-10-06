import logging
import traceback

from musicfield import settings
from apps.api.v1.publish.mqtt import MQTTHandler


def on_connect(mqttc, obj, rc):
    mqttc.subscribe("$SYS/#", 0)
    print("rc: " + str(rc))


def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
    print(string)

class PushService(MQTTHandler):

    def __init__(self):
        super().__init__()
        if settings.DEBUG and False:
            self.mqttc.on_log = on_log
            self.mqttc.on_message = on_message
            self.mqttc.on_connect = on_connect
            self.mqttc.on_publish = on_publish
            self.mqttc.on_subscribe = on_subscribe

    '''
        msg = {'topic':"<topic>", 'payload':"<payload>", 'qos':<qos>,
              'retain':<retain>}
        msgs = [{'topic': "paho/test/multiple", 'payload': "multiple 1"},
                ("paho/test/multiple", "multiple 2", 0, False)]
    '''

    def publish(self, metric, qos=None, retain=None):
        """
        Process a metric by converting metric name to MQTT topic name;
        the payload is metric and timestamp.
        """
        try:
            try:
                self.lock.acquire()
                return MQTTHandler().publish(metric, qos, retain)
            except Exception as e:
                logging.error(traceback.format_exc())
        finally:
            if self.lock.locked():
                self.lock.release()

    def disconnect(self):
        logging.debug("MQTTHandler: reconnecting to broker...")
        self.mqttc.reconnect()

