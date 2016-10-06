"""
Provides a way of serializing and deserializing the account app model
instances into representations such as json.
"""
from rest_framework import serializers

from apps.friendship.contrib.suggestions.models import ImportedContact
from apps.friendship.models import Friend
from apps.api.v1.rest import serializers as custom_serializers
from apps.api.models import Group, User


class CountSerializer(serializers.Serializer):
    count = serializers.IntegerField()


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer to be used for getting and updating groups.
    """

    # url field should lookup by 'name' not the 'pk'
    url = serializers.HyperlinkedIdentityField(
        view_name='v1:group-detail',
        lookup_field='pk'
    )

    is_owner = serializers.SerializerMethodField()

    # an untyped Field class, in contrast to the other typed fields such as
    # CharField, is always read-only.
    # it will be used for serialized representations, but will not be used for
    # updating model instances when they are deserialized
    avatar_thumbnail = custom_serializers.CustomFileField()
    avatar = custom_serializers.CustomFileField()

    class Meta:
        model = Group
        fields = ('url', 'id', 'name', 'is_owner',
                  'avatar_thumbnail', 'avatar', 'likes_count',
                  'created_at', 'last_modified')
        read_only_fields = ('id', 'name', 'likes_count', 'created_at',
                            'last_modified')

    def validate_avatar(self, attrs, source):
        """
        Check that the uploaded file size is within allowed limits

        //TODO combine
        imgfile = attrs.get(source, False)
        if imgfile and imgfile.size > settings.MAX_IMAGE_SIZE:
            raise serializers.ValidationError(
                "Ensure this file's size is at most %s (it is %s)."
                % (human_readable_size(settings.MAX_IMAGE_SIZE),
                   human_readable_size(imgfile.size)))
        """

        return attrs

    def get_is_owner(self, obj):
        """
        get if current requester is group owner
        """
        return self.context['request'].user == obj.owner


class FriendshipSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='v1:friendship-detail',
    )

    from_user_url = serializers.HyperlinkedIdentityField(
        view_name='v1:user-detail',
        lookup_field='from_user',
        lookup_url_kwarg='username',
    )

    to_user_url = serializers.HyperlinkedIdentityField(
        view_name='v1:user-detail',
        lookup_field='to_user',
        lookup_url_kwarg='username',
    )

    class Meta:
        model = Friend
        fields = ('url', 'from_user_url', 'to_user_url', 'created')


class GroupContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name', 'ctime', 'avatar', 'signa', 'area')


class Detail(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value


class DetailSerializer(serializers.Serializer):
    name = serializers.IntegerField()
    value = serializers.CharField(max_length=45)

    def is_valid(self, raise_exception=False):
        return True

    def to_representation(self, instance):
        return {
            'name': instance.name,
            'value': instance.value
        }


class FriendContactSerializer(serializers.ModelSerializer):
    '''
    public static final int DATA_TYPE_EMAIL			= 0;
    public static final int DATA_TYPE_PHONE			= 1;
    public final static int DATA_TYPE_BIRTH         = 2;
    public final static int DATA_TYPE_SIGNA         = 3;
    public final static int DATA_TYPE_GENDER        = 4;
    public final static int DATA_TYPE_AREA          = 5;
    public final static int DATA_TYPE_CAREER        = 6;
    '''
    avatar = custom_serializers.CustomFileField()

    def to_representation(self, instance):
        serializer = DetailSerializer(
            many=True, data=[
                Detail(0, instance.email),
                Detail(1, instance.phone),
                Detail(2, instance.birth),
                Detail(3, instance.signa),
                Detail(4, instance.sex),
                Detail(5, instance.area),
                Detail(6, instance.career)
            ])
        if serializer.is_valid() or True:
            return {
                'id': instance.id,
                'name': instance.name,
                'avatar': instance.avatar.name,
                'ctime': instance.ctime,
                'details': serializer.data
            }

    class Meta:
        model = User
        fields = (
            'id', 'name', 'avatar', 'ctime', 'sex', 'email', 'phone', 'birth', 'signa', 'area', 'career')


class ContactSerializer(serializers.ModelSerializer):
    avatar = custom_serializers.CustomFileField()

    def to_representation(self, instance):
        serializer = DetailSerializer(
            many=True, data=[
                Detail(0, instance.email),
                Detail(1, instance.phone),
                Detail(2, instance.birth),
                Detail(3, instance.signa),
                Detail(4, instance.sex),
                Detail(5, instance.area),
                Detail(6, instance.career)
            ])
        if serializer.is_valid() or True:
            return {
                'id': instance.id,
                'name': instance.name,
                'avatar': instance.avatar.name,
                'ctime': instance.ctime,
                'details': serializer.data
            }

    class Meta:
        model = ImportedContact
        fields = ('id', 'avatar', 'name', 'ctime', 'sex', 'email', 'phone', 'birth', 'signa', 'area', 'career')
