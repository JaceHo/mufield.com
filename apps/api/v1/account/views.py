from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, parsers

from apps.api.models import User, Field, Post, Torrent, MusicUser, ACL
from apps.api.v1.account.permissions import IsOwnerOrReadOnly
from apps.api.v1.account.serializers import UserCreationSerializer, \
    UserSerializer, PostCreationSerializer, PostSerializer, SimilarUserSerializer, \
    PhoneVerifySerializer, UserUpdateSerializer, UserDistanceSerializer, TopicsSerializer
from apps.api.v1.account.serializers import UserPublicOnlySerializer, GeographySerializer
from apps.api.v1.music.serializers import FieldSerializer, FieldUpdateSerializer, TorrentSerializer, \
    TorrentUpdateSerializer, \
    MusicUserSerializer, MusicUserUpdateSerializer, MusicUserCreationSerializer
from apps.api.v1.rest import generics as custom_generics





# Create your views here.

class UserList(generics.ListCreateAPIView):
    """
    List all users or create a new user.
    
    ## Reading
    You can read using this endpoint if you are an user


    ### Fields
    If reading this endpoint returned a list of user objects, each user object
    would only contains public user data.

    Name               | Description                          | Type
    ------------------ | ---------------------------------- |----------
    `url`              | URL of user object                   | _url_
    `moment`|           the moment string for user| _string_
    `sex`       | sex of user object             |_choice_ "M" or "F"
    `date_joined` | date time the user joined | _date/time_
    `username`         | username of user object              |_string_
    `name`         | nickname of user object              |_string_
    `is_friend_or_self`| whether request user is friend of this user object|_boolean_
    `liked_artist_url`|URL of user's liked artist | _url_
    `last_listened_song_url`|URL of user's last listened song| _url_
    `last_stayed_field_url`|URL of user's last stayed field| _url_
    `avatar_thumbnail` | URL of user's thumbnail-sized avatar |_url_
    `last_modified` | last modified date of user object    | _date/time_
    `geo_time`    | last modified time of user geo location| _date/time_
    `latitude` |  latitude of geo location | _decimal_
    `longitude` | longitude of geo location | _decimal_

    ## Publishing
    ### Permissions
    * Anyone can create using this endpoint.
    
    ### Fields

    Parameter  | Description                                       | Type
    ---------- | ------------------------------------------------- | ----------
    `password` | password for the new user. This field is required | _string_
    `phone`    | phone for the new user. This field is a must     | _string_
    `verify_code`| *[coming soon] | _string_

    ### Response
    If create is `successful`, a default success message with code `201`, otherwise an error
    message. 

    
    ## Deleting
    You can't delete using this endpoint
    
    
    ## Updating
    You can't update using this endpoint
    
    
    ## Endpoints
    Name                      | Description                       
    ------------------------- | ----------------------------------------
    `<username>/`             | Retrieve [or update details?] of a public user instance
    
    ##
    """
    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.all()

    def get_serializer_class(self):
        """
        a POST request implies a user creation so return the serializer for
        user creation. 
        All other requests will be GET so use the privacy-respecting user 
        serializer
        """
        if self.request.method == "POST":
            return UserCreationSerializer
        else:
            return UserPublicOnlySerializer


# -----------------------------------------------------------------------------
# USER'S DETAILS AND ASSOCIATED LISTS
# -----------------------------------------------------------------------------

class UserDetail(generics.RetrieveAPIView):
    parser_classes = (parsers.JSONParser, parsers.FileUploadParser,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)
    queryset = User.objects.all()

    # lookup by 'username' not the 'pk' but allow for case-insensitive lookups
    lookup_field = 'username__iexact'
    lookup_url_kwarg = 'username'

    def get_serializer_class(self):
        """
        You only get to see private data if you request details of yourself.
        Otherwise you get to see a limited view of another user's details
        """
        # I purposely dont call self.get_object() here so as not to raise
        # permission exceptions.
        serializer_class = UserPublicOnlySerializer
        # try:
        # lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        # filter = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        # user_object = User.objects.get(**filter)
        # if self.request.user == user_object:
        # serializer_class = UserSerializer
        # except Exception:
        # pass  # serializer_class already setup

        return serializer_class

    # unused function
    def mufield_get_object(self):
        """
        try getting an object by username, and if that fails try getting an
        object by pk.
        """
        from django.shortcuts import get_object_or_404

        queryset = self.get_queryset()
        try:
            obj = User.objects.get(username__iexact=self.kwargs['username'])
        except User.DoesNotExist:
            obj = get_object_or_404(queryset, pk=self.kwargs['username'])

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj


class UserFieldList(generics.ListCreateAPIView):
    """
    List all music field of a user.

    ## Reading
    ### Permissions
    * Only authenticated users viewing their own `fields` sub-collection can
      read this endpoint.

    ### Fields
    Reading this endpoint returns a list of
    [field User objects](/api/v1/users/).


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
            return FieldSerializer
        else:
            return FieldUpdateSerializer

    def get_queryset(self):
        """
        This view should return a list of all fields of the user as determined
        by the lookup parameters of the view.
        """
        return Field.objects.all().filter(user=self.request.user)

    def get_paginate_by(self):
        """
        Return all contacts of the user.
        If there are no objects use the default paginate_by.
        """
        # we can't just use a count() query as get_queryset() actually
        # returns a list not a queryset
        count = len(self.get_queryset())
        return count if (count > 0) else self.paginate_by


class UserFieldTorrentList(generics.ListCreateAPIView, custom_generics.DestoryAPIView):
    """
    List all music torrent of a user field.

    ## Reading
    ### Permissions
    * Only authenticated user fields viewing their own `contacts` sub-collection can
      read this endpoint.

    ### Fields
    Reading this endpoint returns a list of
    [torrent User objects](/api/v1/user fields/).


    ## Publishing
    You can't create using this endpoint


    ## Deleting
    ### endpoints
    ### DELETE `url'?pk=1
    You can delete using this endpoint by specify the pk here


    ## Updating
    You can't update using this endpoint

    """

    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        queryset = self.filter_queryset(self.get_queryset())

        filter_kwargs = {'pk': self.request.query_params['pk']}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'DELETE':
            return TorrentUpdateSerializer
        else:
            return TorrentSerializer

    def get_queryset(self):
        """
        This view should return a list of all fields of the user as determined
        by the lookup parameters of the view.
        """
        if self.request.method == 'POST':
            return Torrent.objects.none()
        else:
            lookup_value = self.kwargs[self.lookup_field]
            field = Field.objects.get(pk=lookup_value)
            return Torrent.objects.all().filter(field=field)

    def get_paginate_by(self):
        """
        Return all contacts of the user.
        If there are no objects use the default paginate_by.
        """
        # we can't just use a count() query as get_queryset() actually
        # returns a list not a queryset
        count = len(self.get_queryset())
        return count if (count > 0) else self.paginate_by


# -----------------------------------------------------------------------------
# AUTHENTICATED USER'S DETAILS AND ASSOCIATED LISTS
# -----------------------------------------------------------------------------

class AuthenticatedUserDetail(custom_generics.RetrievePartUpdateAPIView):
    """
    Retrieve or update an authenticated user instance

    ## Reading
    ### Permissions
    * Authenticated users reading their own user instance get additional private
      data.

    ### Fields
    Reading this endpoint returns a user object containing the private user data.
    An authenticated user reading their own user also gets to see the private
    user data.

    Name               | Description                          | Type
    ------------------ | ---------------------------------- |----------
    `url`              | URL of user object                   | _url_
    `moment`|           the moment string for user| _string_
    `sex`       | sex of user object             |_choice_ "M" or "F"
    `date_joined` | date time the user joined | _date/time_
    `username`         | username of user object              |_string_
    `name`         | nickname of user object              |_string_
    `is_friend_or_self`| whether request user is friend of this user object|_boolean_
    `avatar` | URL of user's thumbnail-sized avatar |_url_
    `avatar_thumbnail` | URL of user's thumbnail-sized avatar |_url_
    `liked_artist_url`|URL of user's liked artist | _url_
    `last_listened_song_url`|URL of user's last listened song| _url_
    `last_stayed_field_url`|URL of user's last stayed field| _url_
    `fields_url`|URL of user's music fields| _url_
    `chats_url`|URL of user's chats| _url_
    `requests_url`|URL of user's friends requests| _url_
    `friends_url`|URL of user's friends | _url_
    `similar_url`|URL of user's similar users| _url_
    `nearby_url`|URL of user's nearby users| _url_
    `posts_url`|URL of user's posts| _url_
    `user_musics_url`|URL of user's music cloud| _url_
    `last_modified`    | last modified date of user object    | _date/time_
    `geo_time`    | last modified time of user geo location| _date/time_
    `latitude` |  latitude of geo location | _decimal_
    `longitude` | longitude of geo location | _decimal_

    ## Publishing
    You can't create using this endpoint


    ## Deleting
    You can't delete using this endpoint


    ## Updating
    Submitting an avatar requires capturing a photo via file upload as
    **multipart/form-data** then using the `avatar` parameter.

    Note that the request method must still be a PUT/PATCH

    ### Permissions
    * Only authenticated users can write to this endpoint.
    * Authenticated users can only update their own user instance.

    ### Response
    If update is successful, a user object containing public and private data,
    otherwise an error message.

    ##
    """

    parser_classes = (parsers.JSONParser, parsers.MultiPartParser,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        else:
            return UserUpdateSerializer

    def get_object(self):
        """
        Simply return authenticated user.
        No need to check object level permissions
        """
        return self.request.user


class UserSimilarList(generics.ListAPIView):
    """
    List all similar users authenticated user located in.

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
        return SimilarUserSerializer

    def get_queryset(self):
        """
        This view should return a list of all similar users for the user as determined
        by the lookup parameters of the view.
        Be sure to exclude expired groups.
        """
        return User.objects.user_similar()


class UserNearbyList(generics.ListAPIView, custom_generics.PartialUpdateAPIView):
    """
    List all nearby users authenticated user located in.

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
            return UserDistanceSerializer
        else:
            return GeographySerializer

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        """
        This view should return a list of all nearby users for the user as determined
        by the lookup parameters of the view.
        Be sure to exclude expired groups.
        """
        if self.request.method == 'GET':
            return User.objects.user_nearby(pk=self.request.user.pk)
        return [self.request.user]

    def get_paginate_by(self):
        """
        Return all fields the user have.
        If there are no objects use the default paginate_by.
        """
        count = self.get_queryset().count()
        return count if (count > 0) else self.paginate_by


class UserPostList(generics.ListCreateAPIView):
    """
    List all posts of a user.

    ## Reading
    ### Permissions
    * Only authenticated users viewing their own `posts` sub-collection can
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
            return PostSerializer
        elif self.request.method == 'POST':
            return PostCreationSerializer

    def get_queryset(self):
        """
        This view should return a list of all posts of the user as determined
        by the lookup parameters of the view.
        """
        return Post.objects.all()

    def get_paginate_by(self):
        """
        Return all posts of the user.
        If there are no objects use the default paginate_by.
        """
        # we can't just use a count() query as get_queryset() actually
        # returns a list not a queryset
        count = len(self.get_queryset())
        return count if (count > 0) else self.paginate_by


class VerifiedActionView(generics.CreateAPIView):
    '''
    This view should call sms send API to send sms to the phones for phone verification
    ##*Note*
     *currently set sms verify code to "666666" will pass this test*
    '''

    permission_classes = (permissions.AllowAny,)

    def get_serializer_class(self):
        return PhoneVerifySerializer


class UserFieldDetail(custom_generics.RetrievePartUpdateDestroyAPIView):
    """
    Get|partial update| destroy a field of the user.

    ## Reading
    ### Permissions
    * Only authenticated users viewing their own `field` sub-collection can
      read this endpoint.

    ### Fields
    It's not good for fields listing

    ## Publishing
    You can create using this endpoint


    ## Deleting
    You can delete using this endpoint


    ## Updating
    You can update using this endpoint

    """

    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        lookup_value = self.kwargs[self.lookup_field]
        return Field.objects.all().filter(pk=lookup_value)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return FieldSerializer
        else:
            return FieldUpdateSerializer


class UserMusicList(generics.ListCreateAPIView):
    """
    List all musics of a user as a private music cloud

    ## Reading
    ### Permissions
    * Only authenticated users viewing their own `fields` sub-collection can
      read this endpoint.

    ### Musics
    Reading this endpoint returns a list of
    [field User objects](/api/v1/users/).


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
            return MusicUserSerializer
        else:
            return MusicUserCreationSerializer

    def get_queryset(self):
        """
        This view should return a list of all fields of the user as determined
        by the lookup parameters of the view.
        """
        return MusicUser.objects.all().filter(user=self.request.user)

    def get_paginate_by(self):
        """
        Return all contacts of the user.
        If there are no objects use the default paginate_by.
        """
        # we can't just use a count() query as get_queryset() actually
        # returns a list not a queryset
        count = len(self.get_queryset())
        return count if (count > 0) else self.paginate_by


class UserMusicDetail(custom_generics.RetrievePartUpdateDestroyAPIView):
    """
    Get|partial update| destroy a field of the user.

    ## Reading
    ### Permissions
    * Only authenticated users viewing their own `field` sub-collection can
      read this endpoint.

    ### Musics
    It's not good for fields listing

    ## Publishing
    You can create using this endpoint


    ## Deleting
    You can delete using this endpoint


    ## Updating
    You can update using this endpoint

    """

    def get_queryset(self):
        lookup_value = self.kwargs[self.lookup_field]
        return MusicUser.objects.all().filter(pk=lookup_value)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MusicUserSerializer
        else:
            return MusicUserUpdateSerializer


class UserTopicList(generics.RetrieveAPIView):
    def get_object(self):
        user = self.request.user
        return ACL.objects.filter((Q(username=user.username) | Q(username='*')) & Q(rw__gt=0)).select_related(
            'topic').all()

    def get_serializer_class(self):
        return TopicsSerializer
