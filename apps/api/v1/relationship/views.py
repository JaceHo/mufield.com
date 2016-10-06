from datetime import timedelta

from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import parsers
from rest_framework.views import APIView
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils import timezone

from rest_framework import generics

from apps.friendship.contrib.suggestions.models import ImportedContact
from apps.friendship.models import Friend
from apps.api.models import Group, Message, User
from apps.api.v1.account.permissions import IsDetailOwner
from apps.api.v1.account.serializers import UserPublicOnlySerializer
from apps.api.v1.rest import generics as custom_generics
from apps.api.v1.conversation.permissions import IsOwnerOrReadOnly
from apps.api.v1.relationship.serializers import GroupSerializer, FriendshipSerializer, GroupContactSerializer, \
    FriendContactSerializer, ContactSerializer


class UserFriendList(generics.ListAPIView):
    """
    List all friends of a user.

    ## Reading
    ### Permissions
    * Only authenticated users viewing their own `friends` sub-collection can
      read this endpoint.

    ### Fields
    Reading this endpoint returns a list of
    [friend User objects](/api/v1/users/).

    Each friend object only contains the friend's public data. You get the
    user's  relationship with each friend from ejabberd.


    ## Publishing
    You can't create using this endpoint


    ## Deleting
    You can't delete using this endpoint


    ## Updating
    You can't update using this endpoint

    """

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserPublicOnlySerializer

    def get_queryset(self):
        """
        This view should return a list of all friends of the user as determined
        by the lookup parameters of the view.
        """

        return Friend.objects.friends(self.request.user)

    def get_paginate_by(self):
        """
        Return all friends of the user.
        If there are no objects use the default paginate_by.
        """
        # we can't just use a count() query as get_queryset() actually
        # returns a list not a queryset
        count = len(self.get_queryset())
        return count if (count > 0) else self.paginate_by


class GroupList(generics.ListAPIView):
    """
    list all musicfield groups

    ## Reading
    ### Permissions
    * Anyone can read this endpoint.

    ### Fields
    Reading this endpoint returns a list of group objects containing public
    group data only.

    Name               | Description                          | Type
    ------------------ | ------------------------------------ | ----------
    `url`              | URL of group object                   | _string_
    `id`               | ID of group object                    | _integer_
    `name`             | (unique) name of group object         | _string_
    `subject`          | group's subject                       | _string_
    `is_owner`         | is current requester the group owner? | _boolean_
    `photo_thumbnail`  | URL of group's thumbnail-sized photo  | _string_
    `photo`            | URL of group's full-sized photo       | _string_
    `location`         | group's associated longitude/latitude | _GEO object_
    `likes_count`      | count of likes group has received     | _integer_
    `created_at`       | group's creation date/time            | _date/time_
    `last_modified`    | last modified date of group object    | _date/time_

    ## Publishing
    You can't create using this endpoint.

    All group creations are done by the ejabberd server.


    ## Deleting
    You can't delete using this endpoint.


    ## Updating
    You can't update using this endpoint

    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = GroupSerializer

    def get_queryset(self):
        """
        Don't return expired groups
        """

        earliest_date = timezone.now() - timedelta(
            seconds=settings.GROUP_EXPIRY_TIME_SECONDS)
        return Group.objects.all().filter(created_at__gte=earliest_date)


class GroupDetail(custom_generics.RetrievePartUpdateDestroyAPIView):
    """
    Retrieve or update a group instance

    ## Reading
    ### Permissions
    * Anyone can read this endpoint.

    ### Fields
    Reading this endpoint returns a group object containing the public group data.

    Name               | Description                          | Type
    ------------------ | ------------------------------------ | ----------
    `url`              | URL of group object                   | _string_
    `id`               | ID of group object                    | _integer_
    `name`             | (unique) name of group object         | _string_
    `subject`          | group's subject                       | _string_
    `is_owner`         | is current requester the group owner? | _boolean_
    `photo_thumbnail`  | URL of group's thumbnail-sized photo  | _string_
    `photo`            | URL of group's full-sized photo       | _string_
    `location`         | group's associated longitude/latitude | _GEO object_
    `likes_count`      | count of likes group has received     | _integer_
    `created_at`       | group's creation date/time            | _date/time_
    `last_modified`    | last modified date of group object    | _date/time_

    #
    _`location` GEO object_ is of the format:

        "location": {
            "type": "Point",
            "coordinates": [-123.0208, 44.0464]
        }

    Note that the coordinates are of format `<longitude>, <latitude>`

    ## Publishing
    You can't write using this endpoint


    ## Deleting
    Ideally we would prevent deletions using this endpoint and leave all
    deletions to the ejabberd server.

    ### Permissions
    * Only authenticated users can delete groups they own

    ### Response
    If deletion is successful, HTTP 204: No Content, otherwise an error message


    ## Updating
    Submitting a photo requires capturing a photo via file upload as
    **multipart/form-data** then using the `photo` parameter.

    Note that the request method must still be a PUT/PATCH

    ### Permissions
    * Only authenticated users can write to this endpoint.
    * Authenticated users can only update groups they own.

    ### Fields
    Parameter    | Description                    | Type
    ------------ | ------------------------------ | ----------
    `subject`    | new subject for the  group      | _string_
    `location`   | new location for the group      | _string_
    `photo`     | new photo for the group. This will be scaled to generate `photo_thumbnail` | _string_

    ### Response
    If update is successful, a group object containing public data,
    otherwise an error message.


    ## Endpoints
    Name                    | Description
    ----------------------- | ----------------------------------------
    `members/<username>/`   | Add/remove authenticated user as a group member

    ##
    """

    parser_classes = (parsers.JSONParser, parsers.MultiPartParser,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def post_save(self, obj, created=False):
        """
        Handle information that is implicit in the incoming update request.
        If this is an authenticated user, then update group's owner to be the
        request's user.
        """
        if (self.request.user.is_authenticated()) and (obj.owner is None):
            obj.owner = self.request.user
            obj.members.add(self.request.user)
            obj.save()


class GroupMemberDetail(generics.GenericAPIView):
    """
    Get if a user is a member of a group, and add or remove them from group.

    ## Reading
    ### Permissions
    * Only authenticated users viewing their own user's membership in a group
      can read this endpoint.

    ### Fields
    If user is a member, **_true_** else **__false__**. Will get an error
    message if group/user don't exist or not authorized for this action.


    ## Publishing
    ### Permissions
    * Only group owner (authenticated user) can add themselves as members of a group.

    ### Fields
    None

    ### Response
    If successful, **_true_**, else an error message.


    ## Deleting
    ### Permissions
    * Only authenticated users can remove themselves as members of a group.

    ### Response
    If successful, **_true_**, else an error message.


    ## Updating
    You can't update using this endpoint

    """

    permission_classes = (permissions.IsAuthenticated, IsDetailOwner)
    serializer_class = UserPublicOnlySerializer
    # IsDetailOwner permission expects to use the lookup field to get the object
    lookup_field = 'username__iexact'
    lookup_url_kwarg = 'username'

    def get(self, request, pk, username, format=None):
        group = get_object_or_404(Group, pk__iexact=pk)
        # IsDetailOwner checks for existence of the user.

        is_group_member = False
        try:
            user = group.members.get(username__iexact=username)
            is_group_member = True
        except User.DoesNotExist:
            pass

        return Response({
            'detail': is_group_member
        })

    def post(self, request, pk, username, format=None):
        group = get_object_or_404(Group, pk__iexact=pk)
        user = get_object_or_404(User, username__iexact=username)
        if group.owner == request.user:
            group.members.add(user)
        else:
            self.permission_denied(request)

        return Response({
            'detail': True
        })

    def delete(self, request, pk, username, format=None):
        group = get_object_or_404(Group, pk__iexact=pk)
        user = get_object_or_404(User, username__iexact=username)
        group.members.remove(user)
        return Response({
            'detail': True
        })


class GroupView(APIView):
    permissions = [IsOwnerOrReadOnly]

    def message_tree(self, qs):
        for msg in qs:
            ser = GroupSerializer(msg)
            data = ser.data
            data['children'] = self.message_tree(msg.responses.all())
            yield data

    def get(self, request, format=None, id=1, page="1"):
        group = get_object_or_404(Group, pk=int(id))
        page = int(page)
        queryset = Message.objects.filter(group=group, responseTo=None).order_by('-id')
        paginator = Paginator(queryset, 10, allow_empty_first_page=True)
        try:
            roots = paginator.page(page)
        except EmptyPage:
            roots = []
        data = self.message_tree(roots)
        return Response(data)


class UserGroupList(generics.ListAPIView):
    """
    List all groups a user participates in.

    ## Reading
    ### Permissions
    * Only authenticated users viewing their own `groups` sub-collection can read
      this endpoint.

    ### Fields
    Reading this endpoint returns a list of [Group objects](/api/v1/groups/)
    containing each group's public data only.


    ## Publishing
    You can't create using this endpoint


    ## Deleting
    You can't delete using this endpoint


    ## Updating
    You can't update using this endpoint

    """

    permission_classes = (permissions.IsAuthenticated, IsDetailOwner,)
    serializer_class = GroupSerializer

    def get_serializer_class(self):
        return GroupSerializer

    def get_queryset(self):
        """
        This view should return a list of all groups for the user as determined
        by the lookup parameters of the view.
        Be sure to exclude expired groups.
        """
        # filter_kwargs = {self.lookup_field: lookup}
        #    user = get_object_or_404(User, **filter_kwargs)
        #    earliest_date = timezone.now() - timedelta(
        #        seconds=settings.GROUP_EXPIRY_TIME_SECONDS)
        return self.request.user.mfgroups.all()  # .filter(created_at__gte=earliest_date)

    def get_paginate_by(self):
        """
        Return all groups the user is a member of.
        If there are no objects use the default paginate_by.
        """
        count = self.get_queryset().count()
        return count if (count > 0) else self.paginate_by


class FriendshipList(generics.ListAPIView):
    """
    List all friendships a user participates in.

    ## Reading
    ### Permissions
    * Only authenticated users viewing their own `friendships` sub-collection can read
      this endpoint.

    ### Fields
    Reading this endpoint returns a list of [Group objects](/api/v1/friendships/)
    containing each friendship's public data only.


    ## Publishing
    You can't create using this endpoint


    ## Deleting
    You can't delete using this endpoint


    ## Updating
    You can't update using this endpoint

    """

    permission_classes = (permissions.IsAuthenticated)
    serializer_class = FriendshipSerializer

    def get_queryset(self):
        """
        This view should return a list of all groups for the user as determined
        by the lookup parameters of the view.
        Be sure to exclude expired groups.
        """
        # filter_kwargs = {self.lookup_field: lookup}
        #    user = get_object_or_404(User, **filter_kwargs)
        #    earliest_date = timezone.now() - timedelta(
        #        seconds=settings.GROUP_EXPIRY_TIME_SECONDS)
        return Friend.objects.all()  # .filter(created_at__gte=earliest_date)

    def get_paginate_by(self):
        """
        Return all groups the user is a member of.
        If there are no objects use the default paginate_by.
        """
        count = self.get_queryset().count()
        return count if (count > 0) else self.paginate_by


class FriendshipDetail(custom_generics.RetrieveAPIView):
    """
    Retrieve or update a friendship instance

    ## Reading
    ### Permissions
    * Anyone can read this endpoint.

    ### Fields
    Reading this endpoint returns a friendship object containing the public friendship data.

    Name               | Description                          | Type
    ------------------ | ------------------------------------ | ----------
    `url`              | URL of friendship object                   | _string_
    `id`               | ID of friendship object                    | _integer_
    `name`             | (unique) name of friendship object         | _string_
    `subject`          | friendship's subject                       | _string_
    `is_owner`         | is current requester the friendship owner? | _boolean_
    `photo_thumbnail`  | URL of friendship's thumbnail-sized photo  | _string_
    `photo`            | URL of friendship's full-sized photo       | _string_
    `location`         | friendship's associated longitude/latitude | _GEO object_
    `likes_count`      | count of likes friendship has received     | _integer_
    `created_at`       | friendship's creation date/time            | _date/time_
    `last_modified`    | last modified date of friendship object    | _date/time_

    #
    _`location` GEO object_ is of the format:

        "location": {
            "type": "Point",
            "coordinates": [-123.0208, 44.0464]
        }

    Note that the coordinates are of format `<longitude>, <latitude>`

    ## Publishing
    You can't write using this endpoint


    ## Deleting
    Ideally we would prevent deletions using this endpoint and leave all
    deletions to the ejabberd server.

    ### Permissions
    * Only authenticated users can delete friendships they own

    ### Response
    If deletion is successful, HTTP 204: No Content, otherwise an error message


    ## Updating
    Submitting a photo requires capturing a photo via file upload as
    **multipart/form-data** then using the `photo` parameter.

    Note that the request method must still be a PUT/PATCH

    ### Permissions
    * Only authenticated users can write to this endpoint.
    * Authenticated users can only update friendships they own.

    ### Fields
    Parameter    | Description                    | Type
    ------------ | ------------------------------ | ----------
    `subject`    | new subject for the  friendship      | _string_
    `location`   | new location for the friendship      | _string_
    `photo`     | new photo for the friendship. This will be scaled to generate `photo_thumbnail` | _string_

    ### Response
    If update is successful, a friendship object containing public data,
    otherwise an error message.


    ## Endpoints
    Name                    | Description
    ----------------------- | ----------------------------------------
    `members/<username>/`   | Add/remove authenticated user as a friendship member

    ##
    """

    permission_classes = (permissions.IsAuthenticated,)
    queryset = Friend.objects.all()
    serializer_class = FriendshipSerializer

class UserGroupContactDetail(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = GroupContactSerializer

    def get_object(self):
        lookup_value = self.kwargs[self.lookup_field]
        return Group.objects.get(pk=lookup_value)

class UserGroupContactList(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = GroupContactSerializer

    def get_queryset(self):
        return self.request.user.mfgroups.all()

    def get_paginate_by(self):
        return self.get_queryset().count()


class UserFriendContactDetail(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FriendContactSerializer

    def get_object(self):
        lookup_value = self.kwargs[self.lookup_field]
        return User.objects.get(pk=lookup_value)

class UserFriendContactList(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FriendContactSerializer

    def get_queryset(self):
        return Friend.objects.friends(self.request.user)

    def get_paginate_by(self):
        return self.get_queryset().count()

class UserContactDetail(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ContactSerializer

    def get_object(self):
        lookup_value = self.kwargs[self.lookup_field]
        return ImportedContact.objects.get(pk=lookup_value)

class UserContactList(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ContactSerializer

    def get_queryset(self):
        return ImportedContact.objects.exclude(phone=None).all()

    def get_paginate_by(self):
        return self.get_queryset().count()
