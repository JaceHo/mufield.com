from __future__ import unicode_literals
import json
import os
from urllib import request
import time

from django.core.files import File
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from imagekit.models import ImageSpecField
from pilkit.processors import SmartResize

from pilkit.processors import Adjust

from mutagen.mp3 import MP3

from apps.friendship.models import FriendshipRequest, Friend
from apps.api.managers import GroupManager, UserManager, ChatManager, MessageManager
from apps.api.v1.fileio.fdfs_storage import FDFSStorage
from apps.api.v1.rest.utils import get_upload_path
from apps.api.signals import *


class Artist(models.Model):
    """
    Description: The musician(s) that create the Music objects.

    """
    name = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['name']
        db_table = 'mf_artist'


class User(AbstractUser):
    ctime = models.IntegerField(max_length=20, default=int(time.time()))
    birth = models.DateField(blank=True, null=True, default=None, )
    signa = models.CharField(max_length=30, null=True, default=None)
    area = models.CharField(max_length=50, null=True, blank=True)
    career = models.CharField(max_length=30, null=True, blank=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+8618012345678'. Up to 15 digits allowed.")
    phone = models.CharField(validators=[phone_regex], blank=False, unique=True, null=False,
                             max_length=16)  # validators should be a list
    # Geo-specific:a geography field (PointField) for
    # location, and overriding the default manager with a instance to
    # perform spatial queries
    latitude = models.DecimalField(decimal_places=20, max_digits=30, null=True, blank=True, default=None)
    longitude = models.DecimalField(decimal_places=20, max_digits=30, null=True, blank=True, default=None)
    geo_time = models.DateTimeField(null=True, blank=True, auto_now_add=True)

    mfgroups = models.ManyToManyField('Group', through='GroupShip', verbose_name=('mfgroups'),
                                      blank=True, help_text=('The musicfield groups this user belongs to. A user will '
                                                             'get all permissions granted to each of '
                                                             'his/her group.'), related_query_name="user")
    liked_posts = models.ManyToManyField('Post', through='PostLiked', verbose_name='liked_posts',
                                         related_name='liked_posts')

    # last modified date to be used by client apps for sync purposes.
    # ref: http://stackoverflow.com/a/5052208
    last_modified = models.DateTimeField(auto_now=True)

    last_online_time = models.DateTimeField(auto_now=True)
    last_listened_song = models.ForeignKey('Music', db_column='last_listened_song', blank=True, null=True,
                                           related_name='loved_users')
    last_stayed_field = models.ForeignKey('Field', db_column='last_stayed_field', blank=True, null=True,
                                          related_name='last_stayed_users')
    liked_artist = models.ForeignKey('Artist', db_column='like_artist', blank=True, null=True,
                                     related_name='followed_users')
    sex = models.CharField(blank=False, default='F', choices=(('M', 'Male'), ('F', 'Female')), max_length=1,
                           help_text='F for female, M for male, default is F(female)')
    is_del = models.BooleanField(blank=False, default=False)
    moment = models.CharField(max_length=45, blank=True)
    invite_code = models.CharField(max_length=45, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    # imagekit spec for avatar shown in mobile app's UITableViews
    avatar = models.ImageField(storage=FDFSStorage(), upload_to='img/avatar', verbose_name="Select Your Profile Image",
                               blank=True, null=True)
    avatar_thumbnail = ImageSpecField(
        source='avatar',
        processors=[SmartResize(width=120, height=120),
                    Adjust(contrast=1.2, sharpness=1.1)],
        format='JPEG',
        options={'quality': 90})

    # this is used for tracking avatar changes
    # ref: http://stackoverflow.com/a/1793323
    __original_avatar = None

    name = models.CharField(blank=True, max_length=20)

    REQUIRED_FIELDS = ['phone', 'email']

    objects = UserManager()

    def get_avatar_thumbnail_url(self):
        """
        get url of avatar's thumbnail. If there isn't an avatar_thumbnail then
        return an empty string
        """
        return self.avatar_thumbnail.url if self.avatar_thumbnail else ''

    def delete_avatar_files(self, instance):
        """
        Delete a user's avatar files in storage
        - First delete the user's ImageCacheFiles on storage. The reason this
          must happen first is that deleting source file deletes the associated
          ImageCacheFile references but not the actual ImageCacheFiles in
          storage.
        - Next delete source file (this also performs a delete on the storage
          backend)

        Arguments:
          - instance: User object instance to have files deleted
        Return:
          None

        Author:

        """
        # get avatar_thumbnail location and delete it
        instance.avatar_thumbnail.storage.delete(instance.avatar_thumbnail.name)
        # delete avatar
        instance.avatar.delete()

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.__original_avatar = self.avatar

    def save(self, *args, **kwargs):
        """
        On instance save ensure old image files are deleted if images are
        updated.

        Arguments:
          - args: all positional arguments
          - kwargs: all keyword arguments
        Return:
          None

        Author:

        """
        if self.__original_avatar and self.avatar != self.__original_avatar:
            # avatar has changed and this isn't the first avatar upload, so
            # delete old files.
            orig = User.objects.get(pk=self.pk)
            self.delete_avatar_files(orig)

        # update the image file tracking properties
        self.__original_avatar = self.avatar

        if self.longitude is not None or self.latitude is not None:
            self.geo_time = timezone.now()
        if self.pk:
            u = User.objects.get(pk=self.pk)
            if u.username != self.username:
                ACL.objects.filter(username=u.username).update(username=self.username)
            if u.name != self.name or u.avatar != self.avatar or self.phone != u.phone or self.sex != u.sex or self.email != u.email or self.area != u.area or self.career != u.career or self.signa != u.signa or self.birth != u.birth:
                self.ctime = int(time.time())
        return super(User, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Default model delete doesn't delete files on storage, so force that to
        happen.

        Arguments:
          - args: all positional arguments
          - kwargs: all keyword arguments
        Return:
          None

        Author:

        """
        # if there were image files, delete those
        if self.avatar:
            self.delete_avatar_files(self)
        ACL.objects.filter(username=self.username).delete()
        super(User, self).delete(*args, **kwargs)

    def __unicode__(self):
        return self.user.username

    class Meta:
        # here for debug toolbar copatibillity
        db_table = 'auth_user'


class ACL(models.Model):
    topic = models.CharField(max_length=100, blank=False)
    username = models.CharField(max_length=30, blank=False, null=False)
    rw = models.IntegerField(db_column='rw', default=0, null=False)

    class Meta:
        unique_together = (('topic', 'username'),)
        db_table = 'auth_acl'


class FieldName(models.Model):
    name = models.CharField(max_length=45, blank=False, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'mf_field_name'


class Field(models.Model):
    user = models.ForeignKey(User, db_column='user', blank=True, null=True, related_name='fields')
    name = models.ForeignKey(FieldName, db_column='name', blank=False, null=False)

    def field_name(self):
        return self.name.name

    class Meta:
        unique_together = (('user', 'name'),)
        db_table = 'mf_field'


class Group(models.Model):
    """
    There's a django standard that suggests we avoid using NULL on string-based
    fields such as CharField and TextField because empty string values will
    always be stored as empty strings, not as NULL so `subject` and `photo` will
    be set to have defaults of '' in the custom SQL script `sql/room.sql`.
    """
    ctime = models.IntegerField(max_length=20, default=int(time.time()))
    signa = models.CharField(max_length=45, null=True, default=None)
    area = models.CharField(max_length=45, null=True, blank=True)
    # DEFAULT SCHEMA FIELDS
    name = models.CharField(null=False, blank=False, max_length=20)

    # date when room was created
    created_at = models.DateTimeField(default=timezone.now())


    # EXTENDED SCHEMA FIELDS
    # members of the chat group.
    members = models.ManyToManyField('User', through='GroupShip', related_name="member_group", null=True,
                                     blank=True)

    likes_count = models.IntegerField(default=0)
    # group's optional representative avatar, TODO combine user avatar
    avatar = models.ImageField(storage=FDFSStorage(), upload_to='img/gavatar/', blank=True)

    # imagekit spec for avatar shown in mobile app's Conversation UITableView
    avatar_thumbnail = ImageSpecField(
        source='avatar',
        processors=[SmartResize(width=120, height=120),
                    Adjust(contrast=1.2, sharpness=1.1)],
        format='JPEG',
        options={'quality': 90}
    )

    # this is used for tracking avatar changes
    # ref: http://stackoverflow.com/a/1793323
    __original_avatar = None

    # last modified date to be used by client apps for sync purposes.
    # for this reason it will not have null=True even though it's an extension
    # of mufield's default schema. So it will have an SQL-level default set
    # ref: http://stackoverflow.com/a/5052208
    last_modified = models.DateTimeField(auto_now=True)

    music = models.ForeignKey('Music', db_column='music', related_name='group_music')
    owner = models.ForeignKey(User, db_column='owner', related_name='created_groups')
    objects = GroupManager()  # custom manager

    def __add_message(self, type, sender, message=None):
        """Generic function for adding a message to the chat group"""
        m = Message(group=self, type=type, author=sender, message=message)
        m.save()
        return m

    def say(self, sender, message):
        """Say something in to the chat group"""
        return self.__add_message('m', sender, message)

    def join(self, user):
        """A user has joined"""
        return self.__add_message('j', user)

    def leave(self, user):
        """A user has leaved"""
        return self.__add_message('l', user)

    def messages(self, after_pk=None, after_date=None):
        """List messages, after the given id or date"""
        m = Message.objects.filter(group=self)
        if after_pk:
            m = m.filter(pk__gt=after_pk)
        if after_date:
            m = m.filter(timestamp__gte=after_date)
        return m.order_by('pk')

    def last_message_id(self):
        """Return last message sent to group"""
        m = Message.objects.filter(group=self).order_by('-pk')
        if m:
            return m[0].id
        else:
            return 0

    def get_avatar_thumbnail_url(self):
        """
        get url of avatar's thumbnail. If there isn't a avatar_thumbnail then
        return an empty string
        """
        return self.avatar_thumbnail.url if self.avatar_thumbnail else ''

    def delete_avatar_files(self, instance):
        """
        Delete an group's avatar files in storage
        - First delete the group's ImageCacheFiles on storage. The reason this
          must happen first is that deleting source file deletes the associated
          ImageCacheFile references but not the actual ImageCacheFiles in
          storage.
        - Next delete source file (this also performs a delete on the storage
          backend)

        Arguments:
          - instance: Group object instance to have files deleted
        Return:
          None
        """
        # get avatar_thumbnail location and delete it
        instance.avatar_thumbnail.storage.delete(instance.avatar_thumbnail.name)
        # delete avatar
        instance.avatar.delete()

    def save(self, *args, **kwargs):
        """
        On instance save ensure old image files are deleted if images are
        updated.

        Arguments:
          - args: all positional arguments
          - kwargs: all keyword arguments
        Return:
          None
        """
        if self.__original_avatar and self.avatar != self.__original_avatar:
            # avatar has changed and this isn't the first avatar upload, so delete
            # old files
            orig = Group.objects.get(pk=self.pk)
            self.delete_avatar_files(orig)

        # update likes count
        try:
            self.likes_count = self.likes.count()
        except:
            pass

        if self.pk:
            u = Group.objects.get(pk=self.pk)
            if u.name != self.name or u.avatar != self.avatar or self.area != u.area or self.signa != u.signa:
                self.ctime = int(time.time())
        super(Group, self).save(*args, **kwargs)
        self.__original_avatar = self.avatar

        GroupShip.objects.create(user=self.owner, group=self)

    def delete(self, *args, **kwargs):
        """
        Default model delete doesn't delete files on storage, so force that to
        happen.

        Arguments:
          - args: all positional arguments
          - kwargs: all keyword arguments
        Return:
          None
        """
        if self.avatar:
            self.delete_avatar_files(self)

        super(Group, self).delete(*args, **kwargs)

    class Meta:
        db_table = 'mf_group'
        ordering = ['-created_at']


class GroupShip(models.Model):
    group = models.ForeignKey(Group, db_column='group', related_name='mfgroups')
    user = models.ForeignKey(User, db_column='user', related_name='user_groups')
    date_joined = models.DateField(auto_now_add=True)
    invite_reason = models.CharField(blank=True, null=True, max_length=64)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if force_insert:
            ACL.objects.get_or_create(username=self.user, topic='mufield/groups/' + self.group.pk, rw=2)
        super(GroupShip, self).save(force_insert, force_update, using, update_fields)

    def delete(self, using=None):
        ACL.objects.get(username=self.user, topic='mufield/groups/' + self.group.pk).delete()
        super(GroupShip, self).delete(using)

    class Meta:
        db_table = 'mf_groupship'


MESSAGE_TYPE_CHOICES = (
    ('s', 'system'),
    ('o', 'operation'),
    ('m', 'message'),
    ('j', 'join'),
    ('l', 'leave'),
    ('n', 'notification'),
    ('i', 'image'),
    ('a', 'audio'),
)

SYNC_STATUS = (
    ('s', 'saved'),
    ('p', 'published'),
)
USER_SYNC_STATUS = (
    ('p', 'processed'),
    ('r', 'read'),
)


class Message(models.Model):
    """
    You cannot update, delete it use this model, use model Chat instead
    """
    chat = models.ForeignKey('Chat', db_column='chat', blank=False, null=False,
                             related_name='chat_messages')  # Field renamed because it was a Python reserved word.
    type = models.CharField(max_length=1, choices=MESSAGE_TYPE_CHOICES, help_text=str(MESSAGE_TYPE_CHOICES))
    created_at = models.DateTimeField(auto_now_add=True)
    audio = models.FileField(blank=True, null=True, storage=FDFSStorage(), upload_to='audio/message')
    image = models.FileField(blank=True, null=True, storage=FDFSStorage(), upload_to='img/message')
    message = models.TextField(blank=True, null=True, max_length=1000)
    author = models.ForeignKey(User, db_column='author', blank=False, null=False,
                               related_name='user_messages')  # Field renamed because it was a Python reserved word.
    sync = models.CharField(max_length=1, blank=True, null=False, default='s', choices=SYNC_STATUS,
                            help_text=str(SYNC_STATUS))
    objects = MessageManager()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.chat.pk is None:
            raise ValueError('cannot add message on null chat, please save it first!')
        if self.pk is not None:
            raise ValueError('cannot update a message')
        if not self.chat.type == 'g' and not Friend.objects.are_friends(self.author,
                                                                        self.chat.friendship if self.chat.type == 'f'
                                                                        else self.chat.request):
            if not self.type == 'm':
                raise ValueError('text message only if you are not friends')
        from apps.api.middlewares import get_current_request

        me = get_current_request().user
        self.author = me

        if self.chat.type == 'r' and not self.chat.chat_messages.count() == 0:
            if self.chat.request.from_user == me:
                raise ValueError('cannot add message if already sent request, doing nothing')
            elif self.chat.request.to_user == me:
                # adding friends, equal to accept request
                self.chat.request.accept()
        add = False
        if not self.pk:
            add = True
        super(Message, self).save(force_insert, force_update, using, update_fields)

        if add:
            message_saved.send(ref=self.chat.pk, t=self.chat.type, instance=self)

    def delete(self, using=None):
        pk = self.pk
        super(Message, self).delete(using)
        message_deleted.send(sender=self, pk=pk)

    def __unicode__(self):
        """Each message type has a special representation, return that representation.
        This will also be translator AKA i18l friendly."""
        if self.type == 's':
            return u'SYSTEM: %s' % self.message
        if self.type == 'n':
            return u'NOTIFICATION: %s' % self.message
        elif self.type == 'j':
            return 'JOIN: %s' % self.author
        elif self.type == 'l':
            return 'LEAVE: %s' % self.author
        elif self.type == 'o':
            return 'OPERATION: %s > %s' % (self.author, self.message)
        elif self.type == 'a':
            return 'AUDIO: %s' % self.audio.url
        elif self.type == 'p':
            return 'IMAGE: %s' % self.image.url
        return self.message

    class Meta:
        unique_together = (('chat', 'author', 'created_at'),)
        db_table = 'mf_message'


class UserMessageStatus(models.Model):
    """
    Through-table that keeps track of the sync-status of messages.
    Upon every message being created, a record of this table must be created
    for every user that is listening in on the chat, excluding the user that
    sent the message.

    OnReceive: if chat is active: setMessageRead(message, user)
    OnChatActivate: setAllMessagesRead(chat.messages, user)
    """
    user = models.ForeignKey('User', null=False)
    chat = models.ForeignKey('Chat', null=True)
    last_message = models.ForeignKey('Message', null=True)
    last_post = models.ForeignKey('Post', null=True)
    sync = models.CharField(max_length=1, blank=True, null=False, default='r', choices=USER_SYNC_STATUS,
                            help_text=str(USER_SYNC_STATUS))

    class Meta:
        db_table = 'mf_message_status'
        unique_together = (('user', 'chat', 'sync', 'last_post'), ('last_post', 'last_message', 'user', 'sync'),)


CHAT_TYPE_CHOICES = (
    ('g', 'group'),
    ('r', 'request'),
    ('f', 'friendship'),
)


class Chat(models.Model):
    type = models.CharField(max_length=1, choices=CHAT_TYPE_CHOICES, help_text=str(CHAT_TYPE_CHOICES), null=False,
                            blank=False)
    request = models.ForeignKey(FriendshipRequest, db_column='request', blank=True, null=True,
                                related_name='request_chat')
    friendship = models.ForeignKey(Friend, db_column='friendship', blank=True, null=True,
                                   related_name='friendship_chat', help_text='from user\'s id small than to user\'s id')
    group = models.ForeignKey(Group, db_column='group', blank=True, null=True,
                              related_name='group_chat')

    objects = ChatManager()

    class Meta:
        unique_together = (('group', 'friendship', 'request'),)
        db_table = 'mf_chat'


class Album(models.Model):
    """
    Description: Every music object is attached to an album even if the album is
                 just a single
    """
    url = models.URLField(name='url', null=True)

    # album title
    title = models.CharField(max_length=200)


    # album art
    art = models.ImageField(storage=FDFSStorage(), upload_to='img/art/', blank=True)

    # imagekit specs for art shown on desktop view of album/playlist collections
    art_small = ImageSpecField(
        source='art',
        processors=[SmartResize(width=132, height=132),
                    Adjust(contrast=1.2, sharpness=1.1)],
        format='JPEG',
        options={'quality': 90})
    # imagekit spec for art shown with music player bar of desktop view.
    art_thumbnail = ImageSpecField(
        source='art',
        processors=[SmartResize(width=60, height=60),
                    Adjust(contrast=1.2, sharpness=1.1)],
        format='JPEG',
        options={'quality': 90})

    # imagekit specs for art shown on mobile view of album/playlist collections
    art_mobile_small = ImageSpecField(
        source='art',
        processors=[SmartResize(width=70, height=70),
                    Adjust(contrast=1.2, sharpness=1.1)],
        format='JPEG',
        options={'quality': 90})
    # imagekit spec for art shown with music player bar of desktop view
    art_mobile_thumbnail = ImageSpecField(
        source='art',
        processors=[SmartResize(width=39, height=39),
                    Adjust(contrast=1.2, sharpness=1.1)],
        format='JPEG',
        options={'quality': 90})

    # imagekit spec for art shown as desktop view's og:image (facebook sharing)
    # and mobile view's (now playing) song-details poster.
    art_display = ImageSpecField(
        source='art',
        processors=[SmartResize(width=320, height=320),
                    Adjust(contrast=1.2, sharpness=1.1)],
        format='JPEG',
        options={'quality': 90})

    # this is used for tracking album art changes
    # ref: http://stackoverflow.com/a/1793323
    __original_art = None

    class Meta:
        ordering = ['title']
        db_table = 'mf_album'

    def __unicode__(self):
        return self.title

    def __init__(self, *args, **kwargs):
        super(Album, self).__init__(*args, **kwargs)
        self.__original_art = self.art

    def with_file_save(self, *args, **kwargs):
        if self.url is not None:
            filename = self.title + '.jpg'
            temp = '/tmp/' + filename
            if not os.path.isfile(temp):
                request.urlretrieve(self.url, temp)  # 将album cover下载到本地
            with open(temp, 'rb') as file:
                self.art.save(get_upload_path(self, filename, '.'), File(file))
                print('album pic saved')

    def delete_art_files(self, instance):
        """
        Description: Delete an album's art files in storage
                     - First delete the user's ImageCacheFiles on storage
                       The reason this must happen first is that deleting source
                       file deletes the associated ImageCacheFile references but
                       not the actual ImageCacheFiles in storage.
                     - Next delete source file (this also performs a delete on
                       the storage backend)

        Arguments:   - instance: Album object instance to have files deleted
        Return:      None

        """
        # get art_thumbnail location and delete it
        instance.art_thumbnail.storage.delete(instance.art_thumbnail.name)
        # do same for art_small
        instance.art_small.storage.delete(instance.art_small.name)
        # delete art
        instance.art.delete()

    def save(self, *args, **kwargs):
        """
        Description: On instance save ensure art files are deleted if art is
                     updated.

        Arguments:   *args, **kwargs
        Return:      None

        """
        if self.__original_art and self.art != self.__original_art:
            # not new art and art changed, so delete old files
            orig = Album.objects.get(pk=self.pk)
            self.delete_art_files(orig)

        super(Album, self).save(*args, **kwargs)
        self.__original_art = self.art

    def delete(self, *args, **kwargs):
        """
        Description: Default model delete doesn't delete files on storage,
                     so force that to happen.

        Arguments:   *args, **kwargs
        Return:      None

        """
        if self.art:
            self.delete_art_files(self)

        super(Album, self).delete(*args, **kwargs)


class Music(models.Model):
    """
    Description: These are the actual songs that people come to this site to
                 listen to.

    """
    artist = models.ForeignKey('Artist', db_column='artist', related_name='songs', blank=True, null=True)
    edition = models.CharField(max_length=45, blank=True)
    title = models.CharField(max_length=128,
                             null=True)

    url = models.URLField(max_length=300, name='url', null=True)
    mp3 = models.FileField(max_length=300, storage=FDFSStorage(), upload_to='music/high/', null=True)
    lrc_url = models.URLField(max_length=300, name='lrc_url', null=True)
    lyrics = models.FileField(max_length=300, storage=FDFSStorage(), upload_to='music/high/', null=True)

    twist = models.IntegerField(default=0, help_text='0 for save, 1 for to be twist, 2 for twisted')

    created_at = models.DateTimeField(auto_now_add=True)

    quality = models.CharField(max_length=1, default='H', choices=(('H', 'high'), ('L', 'low'),),
                               help_text='H for hign quality, L for low quality')

    album = models.ForeignKey('Album', db_column='album', related_name="songs", null=True, blank=True)
    num_plays = models.IntegerField(default=0)  # total number of plays
    last_play = models.DateTimeField(blank=True)
    duration = models.IntegerField(default=0)  # duration in seconds
    html = models.TextField(default='')

    # this is used for mp3 file changes
    # ref: http://stackoverflow.com/a/1793323
    __original_mp3 = None

    class Meta:
        ordering = ['title']
        get_latest_by = 'created_at'

    def __unicode__(self):
        return self.title

    def __init__(self, *args, **kwargs):
        super(Music, self).__init__(*args, **kwargs)
        self.__original_mp3 = self.mp3

    def play_song(self):
        self.set_score(self.num_plays, timezone.datetime.utcnow(), self.last_play)
        self.num_plays += 1
        self.last_play = timezone.datetime.utcnow()
        self.save()

    def set_score(self, num_plays, now, last_play_date):
        """
        Description: Set song ranking score based on recent song plays
                     The algorithm is somewhat based on the ranking performed by
                     Hacker News where each song played in the last
                     `HEAVY_ROTATION_DAYS` days is scored using the formula:
                     Score = (P)/(T+2)^G
                     where,
                       P = number of song plays of an item
                       T = time since last song play
                       G = Gravity
                     Reference: http://amix.dk/blog/post/19574

        Arguments:   num_plays:      number of song plays
                     now:            reference for time since last play
                     last_play_date: last song play datetime

        Return:      None

        Author:      Hippo
        """
        # rememeber we actually want time since last play in hours
        time_since_play = (now - last_play_date).seconds / 3600.0
        self.score = \
            num_plays / (time_since_play + 2.0) ** settings.SONG_RANK_GRAVITY

    def save(self, *args, **kwargs):
        """
        Description:  On song save, if mp3 file is being updated, delete old
                      one from storage.
                      If any mp3 file is being added (new or update), update
                      associated song length

        Arguments:   *args, **kwargs
        Return:      None


        if mp3 file is being changed, update song length
        """
        if self.__original_mp3 and self.mp3 != self.__original_mp3:
            # not new mp3 and mp3 file changed so delete old file
            orig = Music.objects.get(pk=self.pk)
            orig.mp3.delete()

        if self.mp3 != self.__original_mp3:
            # mp3 file change (new or replacement), so update song length
            audio = MP3(self.mp3.file.temporary_file_path())
            self.length = int(audio.info.length)

        super(Music, self).save(*args, **kwargs)
        self.__original_mp3 = self.mp3

    def delete(self, *args, **kwargs):
        """
        Description: On a Music delete, this song will be removed from all
                     playlists it's currently on. So decrement all associated
                     playlist's song counts.
                     In addition to that default model delete doesn't delete
                     files on storage, so force that to happen.

        Arguments:   *args, **kwargs
        Return:      None

        Author:      Hippo
        """
        # decrement all associated playlist's song counts. Be sure that when
        # the playlist is saved it doesn't try to refresh number of songs
        # because this song object hasnt been deleted yet.
        # probably could have just let it refresh num songs if this for-loop
        # was run after super(Music, self).delete()... but it's nice to try
        # something else.

        self.mp3.delete()

        super(Music, self).delete(*args, **kwargs)

    def __unicode__(self):
        result = ""
        if self.title is not None:
            result += self.title
        if self.player is not None:
            result += " " + self.artist.name

        if self.url is not None:
            result += " <a ref='" + self.url + "'>link</a>"

        return result

    def with_file_save(self, *args, **kwargs):
        if self.url is not None:
            filename = self.title + '_' + self.artist.name + '.mp3'
            temp = '/tmp/' + filename
            if not os.path.isfile(temp):
                request.urlretrieve(self.url, temp)  # 将歌曲下载到本地
            with open(temp, 'rb') as file:
                self.mp3.save(get_upload_path(self, filename, '.'), File(file))
                print('mp3 saved')
        if self.lrc_url is not None:
            filename = self.title + '_' + self.artist.name + '.lrc'
            from urllib3 import PoolManager

            obj = json.loads(PoolManager().urlopen('GET', self.lrc_url).data.decode())
            temp = '/tmp/' + filename
            with open(temp, 'wb') as f:
                f.write(obj['lyric'].encode())
            with open(temp, 'r') as file:
                self.lyrics.save(get_upload_path(self, filename, '.'), File(file))
                print('lyrics saved')
        if self.album is not None and self.album.url is not None:
            self.album.with_file_save()
        return self

    class Meta:
        db_table = 'mf_music'
        unique_together = (('title', 'artist'),)


class Post(models.Model):
    liked_users = models.ManyToManyField('User', through='PostLiked', verbose_name=('liked_users'))
    music = models.ForeignKey(Music, db_column='music', blank=True, null=True)
    description = models.TextField(blank=True)
    created_time = models.DateTimeField(auto_now=True)
    modified_time = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, db_column='user', related_name='user_posts')
    attach = models.BooleanField(blank=False, null=False, default=False)
    sync = models.CharField(max_length=1, blank=True, null=False, default='s', choices=SYNC_STATUS,
                            help_text=str(SYNC_STATUS))

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        add = False
        if self.pk is None:
            add = True
        super(Post, self).save(force_insert, force_update, using, update_fields)
        if not add:
            post_updated.send(sender=self)
        else:
            post_saved.send(ref=self.user.pk, instance=self)

    def delete(self, using=None):
        super(Post, self).delete(using)
        post_deleted.send(sender=self, pk=self.pk)

    def __unicode__(self):
        return self.description[:30]

    class Meta:
        db_table = 'mf_post'


class PostLiked(models.Model):
    post = models.ForeignKey(Post, db_column='post', blank=False, null=False)
    user = models.ForeignKey(User, db_column='user', blank=False, null=False)

    class Meta:
        db_table = 'mf_post_liked'


class Attachment(models.Model):
    post = models.ForeignKey(Post, db_column='post', blank=False, null=False, related_name='attachments')
    img = models.FileField(storage=FDFSStorage(), upload_to='img/post/')

    class Meta:
        db_table = 'mf_attachment'


class Torrent(models.Model):
    field = models.ForeignKey(Field, db_column='field', blank=True, null=True, related_name='torrents')
    music_user = models.ForeignKey('MusicUser', db_column='music_user', blank=True, null=True)

    class Meta:
        db_table = 'mf_torrent'


class MusicUser(models.Model):
    user = models.ForeignKey(User, db_column='user', null=False, related_name='user_musics')
    music = models.ForeignKey(Music, db_column='music', null=False,
                              related_name='music_users')
    start = models.DateTimeField(auto_now_add=timezone.datetime.now(), null=False)

    duration = models.IntegerField(max_length=11, default=30, null=False)

    class Meta:
        db_table = 'mf_music_user'
        unique_together = (('user', 'music'),)


FEED_TYPE_CHOICES = (
    ('fb', 'user\'s feed back, no ref'),
    ('fr', 'friend request ref request.pk'),
    ('fa', 'friend request accepted, ref request.pk'),
    ('fd', 'friendship deleted, ref friendship.pk'),
    ('md', 'message delete, ref message.pk'),
    ('mu', 'message update, ref message.pk'),
    ('pd', 'post delete, ref post.pk'),
    ('pu', 'post update, ref post.pk'),
    ('fs', 'friend suggest, ref user.pk'),
)


class Feed(models.Model):
    """
    User Feedback & System feeds
    """
    user = models.ForeignKey('User', blank=False, null=False, related_name='user_feeds')
    body = models.CharField(max_length=1000)
    date_added = models.DateTimeField(default=timezone.now, editable=False)
    type = models.CharField(max_length=2, default='fb', choices=FEED_TYPE_CHOICES, help_text=str(FEED_TYPE_CHOICES))
    ref = models.IntegerField(null=True, blank=True, max_length=11)
    sync = models.CharField(max_length=1, blank=True, null=False, default='s', choices=SYNC_STATUS,
                            help_text=str(SYNC_STATUS))

    class Meta:
        db_table = 'mf_feed'
        ordering = ['-date_added']

    def __unicode__(self):
        return self.body
