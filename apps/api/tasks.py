from datetime import timedelta, datetime

from celery.schedules import crontab
from celery.task import periodic_task
from django.core.serializers import json
from django.db.models import Q, F

from apps.api.config import FRIENDSHIP_TOPIC, GROUP_TOPIC, REQUEST_TOPIC, TWIST_MUSIC_TOPIC, POST_TOPIC
from apps.api.models import Feed
from apps.api.v1.publish.mqtt import Metric
from apps.api.v1.publish.publish import push
from musicfield import celery_app


@periodic_task(run_every=timedelta(seconds=7 * 24 * 60 * 60))
@celery_app.task
def clear_received_messages():
    from apps.api.models import Message, UserMessageStatus

    Feed.objects.filter(Q(sync='p') & ~Q(type='fb')).delete()
    ##TODO clean messages 7 days ago
    # seven_days_ago = datetime.strftime('')
    # Message.objects.filter(Q(sync='p') & Q(F('created_at')>a)).delete()


@periodic_task(run_every=crontab(hour=17, minute=30))
@celery_app.task
def twist_music():
    from apps.api.models import Music

    to_twist = Music.objects.filter(twist=1).all()
    if len(to_twist) < 3:
        to_twist |= Music.objects.filter(twist=0).all()[:3 - len(to_twist)]
    else:
        to_twist = to_twist[:3]
    payload = json.Serializer().serialize(to_twist)
    res = push.publish(Metric(TWIST_MUSIC_TOPIC, payload), retain=True)
    if res and res[0] == 0:
        to_twist.update(twist=2)
