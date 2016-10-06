from rest_framework import serializers
from rest_framework.serializers import raise_errors_on_nested_writes

from apps.api.middlewares import get_current_user
from apps.api.v1.rest import serializers as custom_serializers
from apps.api.models import Artist, Music, FieldName, Torrent, Field, MusicUser


class SingerSerializer(serializers.HyperlinkedModelSerializer):
    followed_users = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='v1:user-detail',
        lookup_field='username'
    )

    class Meta:
        model = Artist
        fields = ('name', 'followed_users')


class MusicSerializer(serializers.HyperlinkedModelSerializer):
    artist = serializers.HyperlinkedIdentityField(
        view_name='v1:artist-detail'
    )

    mp3 = custom_serializers.CustomFileField()

    lyrics = custom_serializers.CustomFileField()

    class Meta:
        fields = ('title', 'artist', 'edition', 'mp3', 'lyrics', 'created_at', 'quality')
        model = Music


class FieldUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=45, allow_blank=False)

    def create(self, validated_data):
        name = FieldName.objects.get_or_create(name=validated_data['name'])[0]
        validated_data['name'] = name
        validated_data['user'] = get_current_user()
        res = serializers.ModelSerializer.create(self, validated_data)
        return res

    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)

        for attr, value in validated_data.items():
            if attr == 'field':
                name = FieldName.objects.get_or_create(name=value)[0]
                setattr(instance, 'name', name)
            else:
                setattr(instance, attr, value)
        instance.save()

        return instance

    class Meta:
        fields = ('name',)
        model = Field


class MusicUserSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='v1:user-music-detail',
        lookup_field='pk',
    )

    music = MusicSerializer(many=False)

    '''
    music_url = custom_serializers.ObjectHyperLinkedIdentityField(
        view_name='v1:music-detail',
        lookup_field='music',
        lookup_url_kwarg='pk',
    )

    user_url = custom_serializers.ObjectHyperLinkedIdentityField(
        view_name='v1:user-detail',
        lookup_field='user',
        lookup_url_kwarg='username',
    )
    '''

    class Meta:
        fields = ('url', 'music', 'start', 'duration')
        model = MusicUser


class TorrentSerializer(serializers.HyperlinkedModelSerializer):
    '''
    field = serializers.HyperlinkedIdentityField(
        view_name='v1:user-field-detail',
        lookup_field='pk'
    )
    '''
    music_user = MusicUserSerializer(many=False, read_only=True)

    class Meta:
        fields = ('music_user',)
        model = Torrent


class FieldSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='v1:user-field-detail',
        lookup_field='pk'
    )
    '''
    user = custom_serializers.ObjectHyperLinkedIdentityField(
        read_only=True,
        required=False,
        view_name='v1:user-detail',
        lookup_field='user',
        lookup_url_kwarg='username',
    )
        serializers.RelatedField(
        many=True,
        read_only=True,
        view_name='v1:user-field-torrent-list',
        lookup_field='pk',
    )
    '''
    torrents = TorrentSerializer(many=True, read_only=True)

    torrents_url = serializers.HyperlinkedIdentityField(
        view_name='v1:user-field-torrent-list',
        lookup_field='pk',
        lookup_url_kwarg='pk',
    )

    name = serializers.SlugRelatedField(
        required=False,
        slug_field='name',
        queryset=FieldName.objects.none(),
    )

    class Meta:
        fields = ('url', 'name', 'torrents', 'torrents_url',)
        model = Field


class TorrentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('music_user', 'field',)
        model = Torrent


class FieldNameSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name',)
        model = FieldName


class MusicUserCreationSerializer(serializers.ModelSerializer):
    start = serializers.DateTimeField()

    def create(self, validated_data):
        validated_data['user'] = get_current_user()
        serializers.ModelSerializer.create(self, validated_data)

    class Meta:
        fields = ('user', 'music', 'start', 'duration')
        model = MusicUser


class MusicUserUpdateSerializer(serializers.ModelSerializer):
    start = serializers.DateTimeField()

    class Meta:
        fields = ('start', 'duration')
        model = MusicUser
