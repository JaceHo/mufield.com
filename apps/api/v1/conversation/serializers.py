"""
Provides a way of serializing and deserializing the conversation app model
instances into representations such as json.
"""
from apps.friendship.models import FriendshipRequest
from rest_framework import serializers

from apps.api.middlewares import get_current_user
from apps.api.models import Message, Chat, User


class FriendshipRequestSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='v1:user-request-detail',
    )
    from_user = serializers.HyperlinkedIdentityField(
        view_name='v1:user-detail',
        lookup_field='from_user',
        lookup_url_kwarg='username',
    )
    to_user = serializers.HyperlinkedIdentityField(
        view_name='v1:user-detail',
        lookup_field='to_user',
        lookup_url_kwarg='username',
    )

    class Meta:
        fields = ('url', 'from_user', 'to_user', 'message', 'created', 'viewed', 'rejected')
        model = FriendshipRequest


class FriendshipRequestCreationSerializer(serializers.ModelSerializer):
    message = serializers.CharField(max_length=200, help_text='max 200 chars')
    to_user = serializers.CharField(help_text='to user username, must be others')

    def create(self, validated_data):
        from_user = get_current_user()
        to_user = User.objects.get(username__iexact=self.data['to_user'])
        message = self.data['message']
        return FriendshipRequest.objects.create(from_user=from_user, to_user=to_user, message=message)

    def validate_to_user(self, attrs):
        try:
            user = User.objects.get(username__iexact=attrs)
            if attrs == get_current_user().username:
                raise serializers.ValidationError("To User with this username must not be your self")
            FriendshipRequest.objects.get(to_user=user.pk, from_user=get_current_user().pk)
            raise serializers.ValidationError("request already sent or been rejected")
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this username does not exists.")
        except FriendshipRequest.DoesNotExist:
            pass
        return attrs

    class Meta:
        model = FriendshipRequest
        fields = ('to_user', 'message')


class MessageSerializer(serializers.ModelSerializer):
    chat_url = serializers.HyperlinkedIdentityField(
        view_name='v1:chat-detail',
    )

    author_url = serializers.HyperlinkedIdentityField(
        view_name='v1:user-detail',
        lookup_field='author',
        lookup_url_kwarg='username'
    )

    class Meta:
        model = Message
        fields = ('id', 'chat_url', 'type', 'created_at', 'sync', 'audio', 'image', 'message', 'author_url')


class ChatSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='v1:chat-detail',
    )

    chat_messages = serializers.HyperlinkedIdentityField(
        view_name='v1:chat-message-list',
    )

    class Meta:
        model = Chat
        fields = ('type', 'url', 'group', 'friendship', 'request', 'chat_messages',)


class ChatMessageCreationSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        author = get_current_user()
        validated_data['author'] = author
        return serializers.ModelSerializer.create(self, validated_data)

    class Meta:
        model = Message
        fields = ('type', 'chat', 'audio', 'image', 'message')
