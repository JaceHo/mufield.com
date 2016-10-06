import logging
import threading
import traceback
from apps.api.celery import app
from musicfield import settings
from apps.api.v1.push.mqtt import MQTTHandler


class PushService(MQTTHandler):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PushService, cls).__new__(cls, *args, **kwargs)
        return cls._instance


    def __init__(self):
        super(PushService, self).__init__()
        if settings.DEBUG:
            self.mqttc.on_log = on_log
            self.mqttc.on_message = on_message
            self.mqttc.on_connect = on_connect
            self.mqttc.on_publish = on_publish
            self.mqttc.on_subscribe = on_subscribe
        threading.Thread(target=self.mqttc.loop_forever, daemon=True).start()


    '''
        msg = {'topic':"<topic>", 'payload':"<payload>", 'qos':<qos>,
              'retain':<retain>}
        msgs = [{'topic': "paho/test/multiple", 'payload': "multiple 1"},
                ("paho/test/multiple", "multiple 2", 0, False)]
    '''

    @app.task
    def publish_async(self, metric, qos=None, retain=None):
        """
        Process a metric by converting metric name to MQTT topic name;
        the payload is metric and timestamp.
        """
        try:
            try:
                self.lock.acquire()
                super(PushService, self).publish(metric, qos, retain)
            except Exception as e:
                logging.error(traceback.format_exc())
        finally:
            if self.lock.locked():
                self.lock.release()

    def publish(self, metric, qos=None, retain=None):
        self.publish_async.apply_async(
            args=(metric, qos, retain),
            retry=True,
            retry_policy={
                'max_retries': 3,
                'interval_start': 0,
                'interval_step': 0.2,
                'interval_max': 0.2,
            }
        )

    def disconnect(self):
        logging.debug("MQTTHandler: reconnecting to broker...")
        self.mqttc.reconnect()


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

