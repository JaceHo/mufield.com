from django.core.exceptions import ValidationError
from rest_framework import mixins, status
from rest_framework.response import Response


class Singleton(object):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance


class UpdateModelMixin(mixins.UpdateModelMixin):
    """
    Modify the default UpdateModelMixin to not create a new object if one isn't
    found for update.
    """

    def update(self, request, *args, **kwargs):
        """
        override the update method of the UpdateModelMixin to *not* create
        an object when it doesn't exist. It's more appropriate in this case
        to return a 404 (does not exist) error.
        """

        partial = kwargs.pop('partial', False)
        self.object = self.get_object()

        serializer = self.get_serializer(self.object,
                                         data=request.DATA,
                                         partial=partial)

        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as err:
            # full_clean on model instance may be called in pre_save,
            # so we have to handle eventual errors.
            return Response(err.message_dict,
                            status=status.HTTP_400_BAD_REQUEST)

        if self.object is None:
            # don't create... simply throw an error
            return Response({'detail': 'Update object Not found'
                             }, status=status.HTTP_404_NOT_FOUND)

        self.object = serializer.save(force_update=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
