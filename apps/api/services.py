import threading

from django.core.serializers import json
from django.db import transaction
from django.db.models import Q

from apps.api.config import GROUP_TOPIC, FRIENDSHIP_TOPIC, REQUEST_TOPIC, POST_TOPIC, TWIST_MUSIC_TOPIC, MUFIELD_FEED
from apps.api.v1.publish.mqtt import Metric
from apps.api.v1.publish.publish import pub_user_topic_request, pub_user_topic_friend, pub_user_topic_post, push
from apps.api.v1.publish.publish import pub_user_topic_group
from apps.api.v1.rest.mixins import Singleton
from musicfield import celery_app

__author__ = 'hippo'


class SyncService(Singleton):
    def __init__(self):
        threading.Thread(name='pub_sync_service', daemon=True, target=self.run).start()

    def run(self):
        pub_sync()
        acl_sync(True)
        feed_sync()


FEED_TYPE_CHOICES = (
    ('fb', 'user\'s feed back, no ref'),
    ('fd', 'friendship deleted, ref friendship.pk'),
    ('md', 'message delete, ref message.pk'),
    ('mu', 'message update, ref message.pk'),
    ('pd', 'post delete, ref post.pk'),
    ('pu', 'post update, ref post.pk'),
    ('fs', 'friend suggest, ref user.pk'),
)


@celery_app.task
def feed_sync(ref=None):
    from apps.api.models import Feed

    if ref is None:
        feeds_pk = Feed.objects.filter(~Q(type='fb'), sync='s').select_related('pk').all()
        for f in feeds_pk:
            with transaction.atomic():
                try:
                    f = Feed.objects.get(pk=f.pk, sync='s')
                    payload = json.Serializer().serialize(f)
                    res = push.publish(Metric(MUFIELD_FEED % f.user.pk, payload))
                    if res and res[0]:
                        f.sync = 'p'
                        f.save()
                except Feed.DoesNotExist:
                    pass
    else:
        if type(ref) is not list:
            refs = [ref]
        else:
            refs = ref
        for ref in refs:
            with transaction.atomic():
                try:
                    feed = Feed.objects.get(ref)
                    if feed.sync == 's':
                        payload = json.Serializer().serialize(feed)
                        res = push.publish(Metric(MUFIELD_FEED % feed.user.pk, payload))
                        if res and res[0]:
                            feed.sync = 'p'
                            feed.save()
                except Feed.DoesNotExist:
                    pass


def pub_sync():
    from apps.api.models import User, Chat

    chats = Chat.objects.select_related('pk').all()
    for pk in chats:
        with transaction.atomic():
            try:
                cc = Chat.objects.get(pk=pk.pk)
                if cc.type == 'r':
                    if cc.chat_messages.count() > 0:
                        pub_user_topic_request(cc.pk)
                elif cc.type == 'g':
                    if cc.chat_messages.count() > 0:
                        pub_user_topic_group(cc.pk)
                elif cc.type == 'f':
                    if cc.chat_messages.count() > 0:
                        pub_user_topic_friend(cc.pk)
            except Chat.DoesNotExist:
                pass
    users = User.objects.select_related('pk').all()
    for pk in users:
        with transaction.atomic():
            try:
                uu = User.objects.get(pk=pk.pk)
                pub_user_topic_post(uu.pk)
            except User.DoesNotExist:
                pass


def acl_sync(with_sys=False):
    from apps.api.models import User, ACL
    from apps.friendship.models import Friend

    users = User.objects.all()
    for u in users:
        if u.username != 'admin':
            gs = u.mfgroups.all()
            topics = []
            for g in gs:
                res = ACL.objects.get_or_create(username=u.username, topic=GROUP_TOPIC % g.pk)
                topics.append(res[0].topic)
                if res[1]:
                    res[0].rw = 2
                    res[0].save()
            ACL.objects.filter(Q(username=u.username) & Q(topic__contains='groups') & ~Q(topic__in=topics)).delete()
            topics.clear()
            for f in Friend.objects.friends(u):
                res = ACL.objects.get_or_create(username=u.username, topic=FRIENDSHIP_TOPIC % f.pk)
                topics.append(res[0].topic)
                if res[1]:
                    res[0].rw = 2
                    res[0].save()
            ACL.objects.filter(
                Q(username=u.username) & Q(topic__contains='friendships') & ~Q(topic__in=topics)).delete()
            topics.clear()
            for r in Friend.objects.sent_requests(u):
                res = ACL.objects.get_or_create(username=u.username, topic=REQUEST_TOPIC % r.pk)
                topics.append(res[0].topic)
                if res[1]:
                    res[0].rw = 1
                    res[0].save()
            for r in Friend.objects.requests(u):
                res = ACL.objects.get_or_create(username=u.username, topic=REQUEST_TOPIC % r.pk)
                topics.append(res[0].topic)
                if res[1]:
                    res[0].rw = 2
                    res[0].save()
            ACL.objects.filter(
                Q(username=u.username) & Q(topic__contains='requests') & ~Q(topic__in=topics)).delete()
            topics.clear()
        if with_sys:
            ACL.objects.get_or_create(username='*', topic=POST_TOPIC, rw=1)
            ACL.objects.get_or_create(username='*', topic=TWIST_MUSIC_TOPIC, rw=1)
