import threading

from django.core.serializers import json
from django.db.models import Q, F

from apps.api.config import REQUEST_TOPIC, FRIENDSHIP_TOPIC, POST_TOPIC, GROUP_TOPIC
from apps.api.v1.publish.mqtt import Metric
from apps.api.v1.publish.push import PushService
from apps.api.v1.rest.mixins import Singleton
from musicfield import celery_app

push = PushService()


@celery_app.task
def pub_user_topic_friend(ref, instance=None):
    from apps.api.models import Message

    if instance is None:
        messages = Message.objects.filter(Q(chat_id=ref) & Q(sync='s'))
        if messages.count() > 0:
            payload = json.Serializer().serialize(messages.all())
            res = push.publish(Metric((FRIENDSHIP_TOPIC % ref), payload))
            if res and res[0] == 0:
                print(res[0], res[1])
                messages.update(sync='p')
    else:
        payload = json.Serializer().serialize(instance)
        res = push.publish(Metric((FRIENDSHIP_TOPIC % instance.pk), payload))
        if res and res[0] == 0:
            instance.update(sync='p')


@celery_app.task
def pub_user_topic_group(ref, instance=None):
    from apps.api.models import Message

    if instance is None:
        messages = Message.objects.filter(Q(chat_id=ref) & Q(sync='s'))
        if messages.count() > 0:
            payload = json.Serializer().serialize(messages.all())
            res = push.publish(Metric((GROUP_TOPIC % ref), payload))
            if res and res[0] == 0:
                print(res[0], res[1])
                messages.update(sync='p')
    else:
        payload = json.Serializer().serialize(instance)
        res = push.publish(Metric((GROUP_TOPIC % instance.pk), payload))
        if res and res[0] == 0:
            instance.update(sync='p')


@celery_app.task
def pub_user_topic_request(ref, instance=None):
    from apps.api.models import Message

    if instance is None:
        messages = Message.objects.filter(Q(chat_id=ref) & Q(sync='s'))
        if messages.count() > 0:
            payload = json.Serializer().serialize(messages.all())
            res = push.publish(Metric((REQUEST_TOPIC % ref), payload))
            if res and res[0] == 0:
                messages.update(sync='p')
    else:
        payload = json.Serializer().serialize(instance)
        res = push.publish(Metric((REQUEST_TOPIC % instance.pk), payload))
        if res and res[0] == 0:
            instance.update(sync='p')


@celery_app.task
def pub_user_topic_post(ref, instance=None):
    from apps.api.models import Post

    if instance is None:
        posts = Post.objects.filter(
            Q(user_id=ref)
            & Q(sync='s')
        )
        if posts.count() > 0:
            payload = json.Serializer().serialize(posts.all())
            res = push.publish(Metric(POST_TOPIC + '/' + str(ref), payload))
            if res and res[0] == 0:
                posts.update(sync='p')
    else:
        payload = json.Serializer().serialize(instance)
        res = push.publish(Metric(POST_TOPIC + '/' + str(instance.pk), payload))
        if res and res[0] == 0:
            instance.update(sync='p')



