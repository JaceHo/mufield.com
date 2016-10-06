from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import UserManager as BaseUserManager
from apps.friendship.models import Friend, FriendshipRequest
from apps.api.middlewares import get_current_user

'''
user field 1 for 5
user field song 1 for 10
user song 1 for 8
'''


def get_user_similarity(user, other):
    u = set(user.fields.all())
    o = set(other.fields.all())
    sfield = u.intersection(o)
    field_mark = len(sfield) * 5
    torrent_mark = 0
    sus = set()
    sos = set()
    for s in sfield:
        su = set(s.torrents.all())
        so = set(s.torrents.all())
        sus = sus.union(su)
        sos = sos.union(so)
        storrent = su.intersection(so)
        torrent_mark += len(storrent) * 10
    same_musics = sus.intersection(sos)
    music_mark = len(same_musics) * 8
    mark = music_mark + field_mark + torrent_mark
    return [mark, same_musics, other]


class UserManager(BaseUserManager):
    """
    Custom model manager for users, this is used for "table-level" operations.
    All methods defined here can be invoked through the User.objects class.
    @see: http://docs.djangoproject.com/en/1.0/topics/db/managers/#topics-db-managers
    Also see GenericTypes from the contenttypes django app!
    @see: http://docs.djangoproject.com/en/1.0/ref/contrib/contenttypes/
    """

    def user_similar(self):
        """
        the public musicfields and song listening similarity
        :param pk:
        :return: similar users
        """

        from apps.api.models import User
        from apps.api.middlewares import get_current_user

        users = User.objects.all().exclude(pk=get_current_user().pk)
        results = map(lambda other: get_user_similarity(get_current_user(), other), users)
        return sorted(results, key=lambda s: s[0])

    def user_nearby(self, pk, distance=50000, limit=15, distance_unit=111.045):
        """
        :param distance: km(unit is 111.045)
        :param limit:
        :param pk: user pk
        :return: user models instances
        """
        from django.db import connection

        # Data retrieval operation - no commit required
        sql = '''
        SELECT id, distance, geo_time
        FROM (
            SELECT
            z.id, z.geo_time,
            z.latitude, z.longitude,
            p.radius,
            p.distance_unit
                * DEGREES(ACOS(COS(RADIANS(p.latpoint))
                * COS(RADIANS(z.latitude))
                * COS(RADIANS(p.longpoint - z.longitude))
                + SIN(RADIANS(p.latpoint))
                * SIN(RADIANS(z.latitude)))) AS distance
            FROM auth_user AS z
            JOIN ( /* these are the query parameters */
                SELECT %s AS latpoint, %s AS longpoint,
                %s*1.0 AS radius, %s AS distance_unit
            ) AS p ON 1=1
        WHERE
            z.latitude IS NOT NULL
            AND z.longitude IS NOT NULL
            AND z.geo_time IS NOT NULL
            AND z.latitude BETWEEN p.latpoint - (p.radius / p.distance_unit)
            AND p.latpoint + (p.radius / p.distance_unit)
            AND z.longitude BETWEEN p.longpoint - (p.radius / (p.distance_unit * COS(RADIANS(p.latpoint))))
            AND p.longpoint + (p.radius / (p.distance_unit * COS(RADIANS(p.latpoint))))
        ) AS d
        WHERE distance <= radius
        ORDER BY distance
        LIMIT %s
        '''
        from apps.api.models import User

        user = User.objects.get(pk=pk)
        if user and user.latitude and user.longitude:
            with connection.cursor() as cursor:
                cursor.execute(sql, [user.latitude, user.longitude, distance, distance_unit, limit])
                return [(row[1], User.objects.get(pk=row[0])) for row in cursor.fetchall()]
        else:
            return []


class GroupManager(models.Manager):
    """
    Custom model manager for groups, this is used for "table-level" operations.
    All methods defined here can be invoked through the Group.objects class.
    @see: http://docs.djangoproject.com/en/1.0/topics/db/managers/#topics-db-managers
    Also see GenericTypes from the contenttypes django app!
    @see: http://docs.djangoproject.com/en/1.0/ref/contrib/contenttypes/
    """

    def create(self, object):
        """Creates a new chat group and registers it to the calling object"""
        r = self.model(content_object=object)
        r.save()
        return r

    def get_for_object(self, object):
        '''Try to get a group related to the object passed.'''
        return self.get(content_type=ContentType.objects.get_for_model(object), object_id=object.pk)

    def get_or_create(self, object):
        """
        Save us from the hassle of validating the return value of get_for_object and create a group if none exists
        """
        from apps.api.models import Group

        try:
            return self.get_for_object(object)
        except Group.DoesNotExist:
            return self.create(object)


class MessageManager(models.Manager):
    # TODO
    def get_unread_from(self, chat, pk=None):
        if chat is None or chat.pk is None:
            raise ValueError('chat should not be none!')
        if pk is not None:
            message = self.get(pk=pk)
            time = message.created_at
            author = message.author
            # status = UserMessageStatus.objects.get(user=author, message=message)
            return self.all().filter(chat=chat, created_at__gt=time).order_by('-created_at')
        else:
            return self.all().filter(chat=chat).order_by('-created_at')

    def get_from(self, chat, pk=None):
        if chat is None or chat.pk is None:
            raise ValueError('chat should not be none!')
        if pk is not None:
            message = self.get(pk=pk)
            time = message.created_at
            self.all().filter(chat=chat, created_at__gt=time).order_by('-created_at')
        else:
            self.all().filter(chat=chat).order_by('-created_at')


class ChatManager(models.Manager):
    '''
    TODO only friends or in gropus may have conversation
    '''

    def add(self, message, group_or_private_ref):
        chat = self.get_or_create(group_or_private_ref)
        if message.author is None or \
                (chat.type == 'g' and chat.group is None) \
                or (chat.type == 'r' and chat.request is None) \
                or (chat.type == 'f' and chat.friendship is None):
            raise ValueError('message author or group or friend(ship) incorrect')
        if message.type == 'i' and message.image is None:
            raise ValueError('message image is none!')
        if message.type == 'a' and message.audio:
            raise ValueError('message audio is none')

        message.chat = chat
        message.save()

    def get_request_message(self, chat):
        from apps.api.middlewares import get_current_request

        request = get_current_request()
        me = request.user
        if not chat.type == 'g':
            from apps.api.models import Message

            messages = Message.objects.get_from(chat)
            if messages and len(messages) == 1 and messages[0].request is not None:
                return messages[0]
            return None
        else:
            raise ValueError('chat must be private type')

    def get_none_empty_chats(self):
        from apps.api.middlewares import get_current_user

        me = get_current_user()
        res = set()
        groups = me.mfgroups.all()
        for g in groups:
            try:
                chat = self.get(group=g)
                messages = chat.chat_messages.all()
                if messages and len(messages) > 0:
                    res.add(chat)
            except:
                pass
        friends = Friend.objects.friends(me)
        for f in friends:
            try:
                if f.pk < me.pk:
                    chat = self.get(friend=Friend.objects.get(from_user=f, to_user=me))
                else:
                    chat = self.get(friend=Friend.objects.get(from_user=me, to_user=f))
                messages = chat.chat_messages.all()
                if messages and len(messages) > 0:
                    res.add(chat)
            except:
                pass
        requests = Friend.objects.requests(me)
        for r in requests:
            try:
                chat = self.get(request=r)
                messages = chat.chat_messages.all()
                if messages and len(messages) > 0:
                    assert len(messages) == 1
                    res.add(chat)
            except:
                pass
        requests = Friend.objects.sent_requests(me)
        for r in requests:
            try:
                chat = self.get(request=r)
                messages = chat.chat_messages.all()
                if messages and len(messages) > 0:
                    assert len(messages) == 1
                    res.add(chat)
            except:
                pass
        return list(res)

    def get_or_create(self, group_or_private_ref):
        """
        Save us from the hassle of validating the return value of get_for_object and create a group if none exists
        """
        from apps.api.models import Group, Chat

        try:
            if isinstance(group_or_private_ref, Group):
                return self.get(group=group_or_private_ref)
            elif isinstance(group_or_private_ref, Friend):
                return self.get(friendship=group_or_private_ref)
            elif isinstance(group_or_private_ref, FriendshipRequest):
                return self.get(request=group_or_private_ref)
        except Chat.DoesNotExist:
            chat = None
            if isinstance(group_or_private_ref, Group):
                chat = Chat(type='g', group=group_or_private_ref)
            elif isinstance(group_or_private_ref, Friend):
                chat = Chat(type='f', friendship=group_or_private_ref)
            elif isinstance(group_or_private_ref, FriendshipRequest):
                chat = Chat(type='r', request=group_or_private_ref)
            if chat:
                chat.save()
                return chat

        raise ValueError('bad request')

    def get_unread_chats(self):

        return self.get_none_empty_chats(True)

    def have_read(self, pk):
        chat = self.get(pk=pk)
        all = chat.chat_messages.all()
        size = len(all)
        n = 0
        while n <= size:
            n += 1
            last = all[-n]
            if last.author != get_current_user():
                break
        if last:
            from apps.api.models import UserMessageStatus

            status = UserMessageStatus.objects.get(user=last.author, message=last)
            if status:
                return status.is_read
        return False
