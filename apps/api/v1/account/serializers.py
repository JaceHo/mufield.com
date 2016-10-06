"""
Provides a way of serializing and deserializing the account app model
instances into representations such as json.
"""

from django.contrib.auth import hashers
from django.core.cache import cache
from apps.friendship.models import Friend
from rest_framework import serializers, status
from rest_framework.authtoken.models import Token

from apps.api.middlewares import get_current_request
from apps.api.utils import int_36_str
from apps.api.v1.music.serializers import MusicSerializer
from apps.api.v1.rest import serializers as custom_serializers
from apps.api.models import User, Post, Music
from apps.api.v1.rest.utils import human_readable_size, get_request_ip
from musicfield import settings


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer to be used for getting and updating users.
    
    Most fields are read-only. Only writeable fields are: 
    - 'phone'
    """
    # url field should lookup by 'username' not the 'pk'
    url = serializers.HyperlinkedIdentityField(
        view_name='v1:user-detail',
        lookup_field='username'
    )

    # username is a RegexField so that we can regulate on accepted characters
    username = serializers.RegexField(
        max_length=30,
        regex=r'^[\w.+-]+$',
        error_messages={'invalid':
                            "Username may contain only letters, numbers and"
                            " ./+/-/_ characters."
                        }
    )

    # an untyped Field class, in contrast to the other typed fields such as
    # CharField, is always read-only. 
    # it will be used for serialized representations, but will not be used for
    # updating model instances when they are deserialized
    avatar_thumbnail = custom_serializers.CustomFileField()
    avatar = custom_serializers.CustomFileField()

    # specify if this user is in requester's friend list
    is_friend_or_self = serializers.SerializerMethodField('get_is_friend')

    # ----------------------
    # Private Fields
    # -----------------------

    # `groups` is a reverse relationship on the User model, so it will not be
    # included by default when using the ModelSerializer class, so we need
    # to add an explicit field for it.
    # show a link to the collection of a user's groups
    groups_url = custom_serializers.NullHyperlinkedIdentityField(
        view_name='v1:user-group-list',
    )

    # show a link to the collection of a user's music fields
    fields_url = custom_serializers.NullHyperlinkedIdentityField(
        view_name='v1:user-field-list',
    )

    nearby_url = custom_serializers.NullHyperlinkedIdentityField(
        view_name='v1:user-nearby-list',
    )

    similar_url = custom_serializers.NullHyperlinkedIdentityField(
        view_name='v1:user-similar-list',
    )

    requests_url = custom_serializers.NullHyperlinkedIdentityField(
        view_name='v1:user-request-list',
    )

    # add max length check to email checks but keep it optional
    email = serializers.EmailField(max_length=254, required=False)

    # show a link to the collection of a user's friends
    friends_url = custom_serializers.NullHyperlinkedIdentityField(
        view_name='v1:user-friend-list',
    )

    chats_url = custom_serializers.NullHyperlinkedIdentityField(
        view_name='v1:user-chat-list',
    )

    musics_url = custom_serializers.NullHyperlinkedIdentityField(
        view_name='v1:user-music-list',
    )

    posts_url = custom_serializers.NullHyperlinkedIdentityField(
        view_name='v1:user-post-list',
    )

    liked_artist_url = custom_serializers.ObjectHyperLinkedIdentityField(
        view_name='v1:artist-detail',
        lookup_field='liked_artist',
        lookup_url_kwarg='pk',
    )

    last_listened_song_url = custom_serializers.ObjectHyperLinkedIdentityField(
        view_name='v1:music-detail',
        lookup_field='last_listened_song',
        lookup_url_kwarg='pk',
    )

    last_stayed_field_url = custom_serializers.ObjectHyperLinkedIdentityField(
        view_name='v1:user-field-detail',
        lookup_field='last_stayed_field',
        lookup_url_kwarg='pk',
    )

    class Meta:
        model = User
        fields = ('pk', 'url', 'moment', 'username', 'avatar_thumbnail',
                  'avatar', 'email', 'is_friend_or_self', 'name', 'liked_artist', 'last_listened_song',
                  'groups_url', 'friends_url', 'chats_url', 'requests_url', 'fields_url',
                  'similar_url', 'nearby_url', 'musics_url', 'posts_url', 'last_stayed_field_url',
                  'last_listened_song_url', 'liked_artist_url',
                  )
        write_only_fields = ('avatar',)
        read_only_fields = ('pk', 'avatar_thumbnail', 'url', 'is_friend_or_self',
                            'groups_url', 'friends_url', 'chats_url', 'requests_url',
                            'fields_url', 'similar_url', 'nearby_url', 'posts_url',
                            'liked_artist_url', 'last_listened_song_url', 'last_stayed_field_url',
                            )
        # lookup by 'username' not the 'pk'
        lookup_field = 'username'

    def validate_avatar(self, imgfile):
        """
        Check that the uploaded file size is within allowed limits
        """
        if imgfile and imgfile.size > settings.MAX_IMAGE_SIZE:
            raise serializers.ValidationError(
                "Ensure this file's size is at most %s (it is %s)."
                % (human_readable_size(settings.MAX_IMAGE_SIZE),
                   human_readable_size(imgfile.size)))

        return imgfile

    def get_is_friend(self, obj):
        """
        Determine if user object is in requester's friend list or is requester.
        """
        user = self.context['request'].user
        if user.is_authenticated():
            if obj == user:
                return True
            friends = Friend.objects.friends(user)
            if obj in friends:
                return True
        return False


class UserUpdateSerializer(UserSerializer):
    """
    Serializer class to show a privacy-respecting version of users, i.e. public
    data only and so doesn't disclose personal information like 'email',
    'groups', 'friends'

    All fields are read-only
    """
    username = serializers.RegexField(
        required=False,
        max_length=30,
        regex=r'^[\w.+-]+$',
        error_messages={'invalid':
                            "Username may contain only letters, numbers and"
                            " ./+/-/_ characters."
                        }
    )

    avatar = serializers.ImageField(
        required=False,
        source='img/avatar',
    )

    class Meta:
        model = User
        fields = (
            'moment', 'sex', 'username', 'name',
            'liked_artist', 'last_listened_song',
            'last_stayed_field', 'email', 'avatar',
        )


class UserPublicOnlySerializer(UserSerializer):
    """
    Serializer class to show a privacy-respecting version of users, i.e. public
    data only and so doesn't disclose personal information like 'email', 
    'groups', 'friends'
    
    All fields are read-only
    """

    class Meta:
        model = User
        fields = (
            'url', 'moment', 'sex', 'date_joined', 'username', 'name', 'is_friend_or_self',
            'avatar_thumbnail', 'moment', 'liked_artist_url', 'last_listened_song_url',
            'last_stayed_field_url', 'geo_time', 'latitude', 'longitude')
        read_only_fields = fields


class UserDistanceSerializer(serializers.Serializer):
    user = UserPublicOnlySerializer()
    distance = serializers.DecimalField(decimal_places=20, max_digits=30)

    def to_representation(self, instance):
        return {
            'user': UserPublicOnlySerializer(instance[1], context={'request': get_current_request()}).data,
            'distance': instance[0]
        }


class SimilarUserSerializer(serializers.Serializer):
    def to_representation(self, obj):
        from apps.api.middlewares import get_current_request

        return {
            'score': obj[0],
            'musics': MusicSerializer(obj[1]).data if not len(obj[1]) == 0 else Music.objects.none(),
            'user': UserPublicOnlySerializer(obj[2], context={'request': get_current_request()}).data,
        }


class UserCreationSerializer(UserSerializer):
    """
    Serializer to be used for creating users.
    """
    password = serializers.CharField(
        style={'input_type': 'password'}
    )

    phone = serializers.RegexField(
        max_length=16,
        error_messages={
            "invalid": "Phone number must be entered in the format: '+8618012345678'. Up to 15 digits allowed."},
        regex=r'^\+?1?\d{9,15}$',
    )

    verify_code = serializers.CharField(
        max_length=6,
        error_messages={
            "invalid": "verify code is incorrect!",
        },
    )

    def validate_verify_code(self, value):
        # TODO
        if value == '666666':
            return value
        request = get_current_request()
        ip = get_request_ip(request)
        if value != cache.get('code' + ip):
            raise serializers.ValidationError("incorrect verify code.")
        else:
            return value

    def create(self, validated_data):
        """
       Instantiate a new User instance.
       """
        phone = validated_data['phone']
        validated_data['username'] = int_36_str(int(phone[3:]))
        validated_data['password'] = hashers.make_password(validated_data['password'], 'seasalt', 'pbkdf2_sha256')
        validated_data.pop('verify_code')
        try:
            User.objects.get(phone=phone)
            User.objects.update(**validated_data)
        except Exception as ex:
            return User.objects.create(**validated_data)

    def to_representation(self, instance):
        return {
            'results': {
                'username': instance.username,
                'auth_token': Token.objects.get(user=instance).key,
                'user_id': instance.pk,
                'code': status.HTTP_201_CREATED,
                'msg': 'ok',
            }
        }

    class Meta:
        model = User
        fields = ('password', 'phone', 'verify_code')
        write_only_fields = fields  # Note: Password field is write-only


class GeographySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('latitude', 'longitude',)


class PostSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Post


class PostCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('music', 'user', 'attachments')


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token


class PhoneVerifySerializer(serializers.Serializer):
    """
    #Serializer to be used for sending verification msg.
    ## 请求示例：
    *http://apistore.baidu.com/astore/serviceinfo/1989.html

    http://222.185.228.25:8000/msm/sdk/http/sendsms.jsp?username=NTY000000&scode=123456&mobile=13805100000&content=你好101540

    JSON返回示例：

    {
        code : 0#数字#数字
    }

    cache


    """

    # phone is a RegexField so that we can regulate on accepted characters
    phone = serializers.RegexField(
        max_length=15,
        regex=r'^\+?1?\d{9,15}$',
        error_messages={
            'invalid': "Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."},
    )

    type = serializers.ChoiceField(
        choices=('reg', 'reset_password')
    )

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        return validated_data

    def is_valid_request(self, phone):
        request = get_current_request()
        ip = get_request_ip(request)
        import time

        curr = time.time()
        if not cache.get(ip + phone) or curr - (cache.get(ip + phone) or 0) > 60 * 1000:
            cache.set(ip + phone, curr)
            return True
        else:
            return False

    def to_representation(self, obj):
        # TODO: integrate sms sending API
        import time

        time.sleep(0.5)
        request = get_current_request()
        ip = get_request_ip(request)
        # TODO
        cache.set('code' + ip, '666666')

        if self.is_valid_request(obj['phone']):
            return {
                'code': 201,
                'msg': ' accepted',
            }
        else:
            return {
                'code': 403,
                'msg': 'only one sms for verify within 60s is allowed',
            }


class TopicsSerializer(serializers.Serializer):
    def to_representation(self, obj):
        return {
            'code': 201,
            'pk': get_current_request().user.pk,
            'topics': [x.topic for x in obj]
        }
