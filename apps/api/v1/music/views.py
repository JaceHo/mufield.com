from rest_framework import viewsets

from apps.api.models import Artist, Music, FieldName
from apps.api.v1.music.serializers import SingerSerializer, MusicSerializer, FieldNameSerializer
from rest_framework import generics


class SingerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Get|partial update| destroy a artist of the user.

    ## Reading
    ### Permissions
    * Only authenticated users viewing their own `artist` sub-collection can
      read this endpoint.

    ### Fields
    Reading this endpoint returns a list of
    [artists objects](/api/v1/artists/).

    ## Publishing
    You can create using this endpoint


    ## Deleting
    You can delete using this endpoint


    ## Updating
    You can update using this endpoint

    """
    queryset = Artist.objects.all()
    serializer_class = SingerSerializer


class MusicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Get|partial update| destroy a music of the user.

    ## Reading
    ### Permissions
    * Only authenticated users viewing their own `music` sub-collection can
      read this endpoint.

    ### Fields
    Reading this endpoint returns a list of
    [musics objects](/api/v1/musics/).

    ## Publishing
    You can create using this endpoint


    ## Deleting
    You can delete using this endpoint


    ## Updating
    You can update using this endpoint

    """
    queryset = Music.objects.all()
    serializer_class = MusicSerializer


class FieldNameListView(generics.ListCreateAPIView):

    def get_serializer_class(self):
        return FieldNameSerializer

    def get_queryset(self):
        return FieldName.objects.all()
