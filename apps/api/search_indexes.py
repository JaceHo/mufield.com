from apps.friendship.models import Friend, FriendshipRequest

from apps.api.models import Group, Music, User
from haystack import indexes
from apps.api.models import Music, Field


class MusicIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Description: Haystack search index for Music model

    Author:      Nnoduka Eruchalu
    """

    text = indexes.EdgeNgramField(document=True, use_template=True)

    def get_model(self):
        return Music


class FieldIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Description: Haystack search index for Field model

    Author:      Nnoduka Eruchalu
    """

    text = indexes.EdgeNgramField(document=True, use_template=True)

    def get_model(self):
        return Field


class UserIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Haystack search index for User model.
    
    This includes the ctime field for use in filtering out expired Groups.
    """

    text = indexes.EdgeNgramField(document=True, use_template=False)

    def get_model(self):
        return User


class GroupIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Haystack search index for Group model.

    This includes the ctime field for use in filtering out expired Groups.
    """

    text = indexes.EdgeNgramField(document=True, use_template=False)
    ctime = indexes.DateTimeField(model_attr='created_at')

    def get_model(self):
        return Group


class MusicIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Haystack search index for Group model.

    This includes the ctime field for use in filtering out expired Groups.
    """

    text = indexes.EdgeNgramField(document=True, use_template=True)
    ctime = indexes.DateTimeField(model_attr='ctime')

    def get_model(self):
        return Music


class FriendIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Haystack search index for User model.

    This includes the ctime field for use in filtering out expired Groups.
    """

    text = indexes.EdgeNgramField(document=True, use_template=True)
    ctime = indexes.DateTimeField(model_attr='ctime')

    def get_model(self):
        return Friend


class FriendShipRequestIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Haystack search index for User model.

    This includes the ctime field for use in filtering out expired Groups.
    """

    text = indexes.EdgeNgramField(document=True, use_template=True)
    ctime = indexes.DateTimeField(model_attr='ctime')

    def get_model(self):
        return FriendshipRequest
