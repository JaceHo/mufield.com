from apps.friendship.models import Friend, FriendshipRequest

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from apps.api.models import Message, Chat, Post
from apps.api.v1.account.serializers import PostSerializer, PostCreationSerializer
from apps.api.v1.conversation.serializers import ChatSerializer, ChatMessageCreationSerializer, \
    FriendshipRequestSerializer, FriendshipRequestCreationSerializer

from apps.api.v1.conversation import serializers
from apps.api.v1.rest import generics as custom_generics

# Create your views here.


class RequestDetailViewPart(custom_generics.RetrievePartUpdateAPIView):
    """
    Retrieve or update(accept, view, reject.etc) the authenticated user request

    ## Reading
    ### Permissions
    * Authenticated users

    ### Fields
    Reading this endpoint returns a user object containing the authenticated
    user's public and private data.

    Name               | Description                          | Type
    ------------------ | ------------------------------------ | ----------
    `url`              | URL of user object                   | _string_
    `from_user`       | from user object, url            | _string_
    `to_user`         | to user object, url              | _string_
    `message`           | message of when request initially created,**_private_**. | _string_


    ## Publishing
    You can's create using this endpoint


    ## Deleting
    You can delete using this endpoint


    ## Updating
    Note that the request method must still be a POST

    ### Permissions
    * Only authenticated users can write to this endpoint.


    ### Response
    If update is successful, a result object containing public and private data,
    otherwise an error message.

    ##
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return FriendshipRequest.objects.all()

    def get_serializer_class(self):
        return serializers.FriendshipRequestSerializer


class UserRequestList(custom_generics.ListCreateAPIView):
    """
    Retrieve or update the authenticated request

    ## Reading
    ### Permissions
    * Authenticated requests

    ### Fields
    Reading this endpoint returns a request object containing the authenticated
    request's public and private data.

    Name               | Description                          | Type
    ------------------ | ------------------------------------ | ----------
    `url`              | URL of request object                   | _string_
    `id`               | ID of request                           | _integer_
    `requestname`         | requestname of request object              | _string_
    `first_name`       | first name of request object            | _string_
    `avatar_thumbnail` | URL of request's thumbnail-sized avatar | _string_
    `email`            | email of request object. **_private_**. | _string_
    `groups_url` | URL of request's groups sub-collection. **_private_**.  | _string_
    `contacts_url` | URL of request's contacts sub-collection. **_private_**. | _string_


    ## Publishing
    You can't create using this endpoint


    ## Deleting
    You can't delete using this endpoint


    ## Updating
    Submitting an avatar requires capturing a photo via file upload as
    **multipart/form-data** then using the `avatar` parameter.

    Note that the request method must still be a PUT/PATCH

    ### Permissions
    * Only authenticated user can write to this endpoint.

    ### Fields
    Parameter    | Description                    | Type
    ------------ | ------------------------------ | ----------
    `first_name` | new first name for the  request   | _string_
    `email`      | new email for the request         | _string_
    `avatar`     | new avatar image for the request. This will be scaled to generate `avatar_thumbnail` | _string_

    ### Response
    If update is successful, a request object containing public and private data,
    otherwise an error message.


    ## Endpoints
    Name                    | Description
    ----------------------- | ----------------------------------------
    [`unread`](?type=unread/)       | All the groups authenticated request is a member of
    [`sents`](?type=sent/)       | All the groups authenticated request is a member of
    [`rejected`](?type=rejected/)  | All authenticated request's friends i.e. friends and friend requests (from and to)
    [`unrejected`](?type=unrejected/)       | All the groups authenticated request is a member of

    ##
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if self.request.method == 'GET':
            if not self.request.query_params.get('type'):
                return Friend.objects.requests(self.request.user)
            elif self.request.query_params.get('type') == 'unread':
                return Friend.objects.unread_requests(user=self.request.user)
            elif self.request.query_params.get('type') == 'sent':
                return Friend.objects.sent_requests(user=self.request.user)
            elif self.request.query_params.get('type') == 'rejected':
                return Friend.objects.rejected_requests(user=self.request.user)
            elif self.request.query_params.get('type') == 'unrejected':
                return Friend.objects.unrejected_requests(user=self.request.user)
        else:
            return FriendshipRequest.objects.none()

    def get_object(self):
        FriendshipRequest.objects.none()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return FriendshipRequestSerializer
        else:
            return FriendshipRequestCreationSerializer


class ChatView(APIView):
    RESPONSE_SUCCESS = {'results': {'code': 200, 'msg': 'Ok'}}

    def delete(self, request, format=None):
        """
        Delete chat
        """
        user_token = Token.get_user_token(request)
        request.user.delete_chat(user_token)

        return Response(self.RESPONSE_SUCCESS)


class UserChatList(generics.ListCreateAPIView):
    """
    List all chats of a user.

    ## Reading
    ### Permissions
    * Only authenticated users viewing their own `chats` sub-collection can
      read this endpoint.

    ### Fields
    Reading this endpoint returns a list of
    [chat User objects](/api/v1/users/).

    Each chat object only contains the chat's public data. You get the
    user's  relationship with each chat from mosquitto.


    ## Publishing
    You can't create using this endpoint


    ## Deleting
    You can't delete using this endpoint


    ## Updating
    You can't update using this endpoint

    """

    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ChatSerializer
        elif self.request.method == 'POST':
            return ChatMessageCreationSerializer

    def get_queryset(self):
        """
        This view should return a list of all chats of the user as determined
        by the lookup parameters of the view.
        """
        return Chat.objects.get_none_empty_chats()

    def get_paginate_by(self):
        """
        Return all chats of the user.
        If there are no objects use the default paginate_by.
        """
        # we can't just use a count() query as get_queryset() actually
        # returns a list not a queryset
        count = len(self.get_queryset())
        return count if (count > 0) else self.paginate_by


class ChatDetail(generics.RetrieveAPIView):
    """
    Retrieve chat of a user or add/delete a message here

    ## Reading
    ### Permissions
    * Only authenticated users viewing their own `chats` sub-collection can
      read this endpoint.

    ### Fields
    Reading this endpoint returns a list of
    [chat User objects](/api/v1/users/).

    Each chat object only contains the chat's public data. You get the
    user's  relationship with each chat from mosquitto.


    ## Publishing
    You can't create using this endpoint


    ## Deleting
    You can't delete using this endpoint


    ## Updating
    You can't update using this endpoint

    """

    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        """
        This view should return a list of all chats of the user as determined
        by the lookup parameters of the view.
        """
        return self.get_object()

    def get_serializer_class(self):
        return ChatSerializer

    def get_paginate_by(self):
        """
        Return all friends of the user.
        If there are no objects use the default paginate_by.
        """
        # we can't just use a count() query as get_queryset() actually
        # returns a list not a queryset
        count = len(self.get_queryset())
        return count if (count > 0) else self.paginate_by


class ChatMessageList(generics.ListCreateAPIView):
    """
    List all authenticated user the chat messages

    ## Reading
    ### Permissions
    * Only authenticated users can read this endpoint.

    ### Fields
    Reading this endpoint returns a list of [User objects](/api/v1/users/)
    containing each user's public data only.


    ## Publishing
    Use `put` method to update user location (eg:latitude, longitude)


    ## Deleting
    You can't delete using this endpoint


    ## Updating
    You can't update using this endpoint

    """
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.MessageSerializer
        else:
            return serializers.ChatMessageCreationSerializer

    def get_queryset(self):
        """
        This view should return a list of all users chat messages for the user as determined
        by the lookup parameters of the view.
        """
        if self.request.method == 'GET':
            # Perform the lookup filtering.
            chat = Chat.objects.get(pk=self.kwargs['pk'])
            return Message.objects.get_unread_from(chat)
        else:
            return Message.objects.none()

    def get_paginate_by(self):
        """
        Return all fields the user have.
        If there are no objects use the default paginate_by.
        """
        count = self.get_queryset().count()
        return count if (count > 0) else self.paginate_by


class PostLikeSerializer(object):
    pass


class PostDetail(generics.RetrieveAPIView):
    permission_classes = (permissions.AllowAny,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PostSerializer
        elif self.request.method == 'POST':
            if self.request.QUERY_PARAMS['like']:
                return PostLikeSerializer


class ChatDetail(generics.RetrieveAPIView):
    """
    Retrieve chat of a user or add/delete a message here

    ## Reading
    ### Permissions
    * Only authenticated users viewing their own `chats` sub-collection can
      read this endpoint.

    ### Fields
    Reading this endpoint returns a list of
    [chat User objects](/api/v1/users/).

    Each chat object only contains the chat's public data. You get the
    user's  relationship with each chat from mosquitto.


    ## Publishing
    You can't create using this endpoint


    ## Deleting
    You can't delete using this endpoint


    ## Updating
    You can't update using this endpoint

    """

    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        """
        This view should return a list of all chats of the user as determined
        by the lookup parameters of the view.
        """

        if self.request.method == 'get':
            return self.get_object()
        elif self.request.method == 'post':
            return Message.objects.none()

    def get_serializer_class(self):
        if self.request.method == 'get':
            return ChatSerializer
        elif self.request.method == 'post':
            return ChatMessageCreationSerializer

    def get_paginate_by(self):
        """
        Return all friends of the user.
        If there are no objects use the default paginate_by.
        """
        # we can't just use a count() query as get_queryset() actually
        # returns a list not a queryset
        count = len(self.get_queryset())
        return count if (count > 0) else self.paginate_by
