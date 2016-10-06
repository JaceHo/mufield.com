from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from django.conf import settings
from apps.friendship.models import Friend
from apps.friendship.signals import friendship_request_preaccepted, \
    friendship_request_created, friend_preadded, friend_preremoved, friendship_removed
from rest_framework.authtoken.models import Token

from apps.api.config import REQUEST_TOPIC, FRIENDSHIP_TOPIC

'''
django-friendship emits the following signals:

friendship_request_created
friendship_request_rejected
friendship_request_canceled
friendship_request_accepted
friendship_removed
follower_created
following_created
follower_removed
following_removedd

#pushlishing
mufield/sys/musics/new
mufield/sys/upgrade
mufield/users/clientId/
mufield/users/clientId/others/otherId/chats/request
mufield/users/clientId/friends/friendId/chats/message
mufield/users/clientId/friends/friendId/posts/new
mufield/users/clientId/friends/friendId/posts/comment
mufield/users/clientId/friends/friendId/posts/like
mufield/users/chientId/groups/groupId/chats/message


subscribing
mufield/users/selfId/others/+/chats/request
mufield/users/selfId/friends/+/chats/message
mufield/users/selfId/groups/+/chats/message
'''

message_saved = Signal()
message_deleted = Signal(providing_args=['pk'])
post_saved = Signal()
post_updated = Signal()
post_commented = Signal()
post_liked = Signal()
post_deleted = Signal(providing_args=['pk'])

'''
pub_user_topic_request.apply_async(
    args=(ref,),
    kwargs=kwargs,
    queue='im',
)
pub_user_topic_friend.apply_async(
    args=(ref,),
    kwargs=kwargs,
    queue='im',
)
pub_user_topic_group.apply_async(
    args=(ref,),
    kwargs=kwargs,
    queue='im',
)
'''


@receiver(message_saved)
def publish_to_chat(ref, t, instance, **kwargs):
    if t == 'r':
        from apps.api.v1.publish.publish import pub_user_topic_request

        pub_user_topic_request(ref, instance)
    elif t == 'f':
        from apps.api.v1.publish.publish import pub_user_topic_friend

        pub_user_topic_friend(ref, instance)

    elif t == 'g':
        from apps.api.v1.publish.publish import pub_user_topic_group

        pub_user_topic_group(ref, instance)


'''
    pub_user_topic_group.apply_async(
        args=(user_ref,),
        kwargs=kwargs,
        queue='im',
    )
'''


@receiver(post_saved)
def publish_post_to_friends(user_ref, instance, **kwargs):
    from apps.api.v1.publish.publish import pub_user_topic_post

    pub_user_topic_post(user_ref, instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(friendship_request_created)
def on_request_created(sender, **kwargs):
    from apps.api.models import Chat, Message
    from apps.api.models import ACL

    chat = Chat.objects.get_or_create(sender)
    Message.objects.create(type='m', author=sender.from_user, chat=chat, message=sender.message)
    ACL.objects.get_or_create(username=sender.from_user.username, topic=REQUEST_TOPIC % sender.pk, rw=1)
    ACL.objects.get_or_create(username=sender.to_user.username, topic=REQUEST_TOPIC % sender.pk, rw=2)


@receiver(friend_preadded)
def on_preadded(sender, **kwargs):
    from apps.api.models import ACL

    ACL.objects.get_or_create(username=sender.to_user, topic=FRIENDSHIP_TOPIC % sender.pk, tw=2)
    ACL.objects.get_or_create(username=sender.from_user, topic=FRIENDSHIP_TOPIC % sender.pk, tw=2)


@receiver(friend_preremoved)
def on_preremoved(sender, **kwargs):
    from apps.api.models import ACL

    ACL.objects.get(username=sender.to_user, topic=FRIENDSHIP_TOPIC % sender.pk, tw=2).delete()
    ACL.objects.get(username=sender.from_user, topic=FRIENDSHIP_TOPIC % sender.pk, tw=2).delete()


@receiver(friendship_request_preaccepted)
def on_preaccepted(sender, from_user, to_user, **kwargs):
    from friendship.models import Friend
    from apps.api.models import Chat

    chat = Chat.objects.get(request=sender)
    chat.type = 'f'
    chat.request = None
    if from_user.pk < to_user.pk:
        chat.friendship = Friend.objects.get(from_user=from_user, to_user=to_user)
    else:
        chat.friendship = Friend.objects.get(from_user=to_user, to_user=from_user)
    chat.save()


@receiver(friendship_removed)
def on_friend_deleted(sender, from_user, to_user, **kwargs):
    from apps.api.models import Feed

    feed = Feed.objects.create(type='fd', user=to_user, ref=sender.pk)
    from apps.api.services import feed_sync

    feed_sync.apply_async(
        args=(feed.pk,),
        kwargs=kwargs,
        queue='default',
    )


# no guratee that client will delete this message since he/she will had seen it
@receiver(message_deleted)
def on_message_delete(sender, pk, **kwargs):
    from apps.api.services import feed_sync
    from apps.api.models import Feed

    refs = []
    if sender.chat.type == 'f':
        to = sender.chat.friendship.to_user if sender.chat.friendship.from_user == sender.author else sender.chat.friendship.from_user
        f = Feed.objects.create(type='md', sync='s', user=to)
        refs.append(f.pk)
    elif sender.chat.type == 'g':
        users = sender.chat.group.members.all()
        for u in users:
            f = Feed.objects.create(type='md', sync='s', user=u)
            refs.append(f.pk)

    feed_sync.apply_async(
        args=(refs,),
        kwargs=kwargs,
        queue='im',
    )


@receiver(post_deleted)
def on_post_deleted(sender, pk, **kwargs):
    from apps.api.services import feed_sync
    from apps.api.models import Feed

    refs = []
    friends = Friend.objects.friends(sender.user)
    for f in friends:
        feed = Feed.objects.create(user=f, type='pd', ref=pk)
        refs.append(feed.pk)
    feed_sync.apply_async(
        args=(refs,),
        kwargs=kwargs,
        queue='im',
    )
