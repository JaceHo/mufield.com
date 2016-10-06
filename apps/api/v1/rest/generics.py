"""
Customize rest_framework generic update views to use custom UpdateModelMixin
"""
from rest_framework import generics, mixins

from apps.api.v1.rest import mixins as custom_mixins


class RetrieveAPIView(generics.GenericAPIView,
                      generics.mixins.RetrieveModelMixin):
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class PartialUpdateAPIView(generics.GenericAPIView,
                           custom_mixins.UpdateModelMixin):
    def post(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class UpdateAPIView(custom_mixins.UpdateModelMixin,
                    generics.GenericAPIView):
    """
    Concrete view for updating a model instance.
    """

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class ListCreateAPIView(mixins.ListModelMixin,
                        generics.GenericAPIView,
                        mixins.UpdateModelMixin):
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class RetrievePartUpdateAPIView(mixins.RetrieveModelMixin,
                                custom_mixins.UpdateModelMixin,
                                generics.GenericAPIView):
    """
    Concrete view for retrieving, updating a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class DestoryAPIView(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin):
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class RetrievePartUpdateDestroyAPIView(mixins.RetrieveModelMixin,
                                       custom_mixins.UpdateModelMixin,
                                       mixins.DestroyModelMixin,
                                       generics.GenericAPIView):
    """
    Concrete view for retrieving, updating or deleting a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class RetrieveUpdateDestroyAPIView(mixins.RetrieveModelMixin,
                                   custom_mixins.UpdateModelMixin,
                                   mixins.DestroyModelMixin,
                                   generics.GenericAPIView):
    """
    Concrete view for retrieving, updating or deleting a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
