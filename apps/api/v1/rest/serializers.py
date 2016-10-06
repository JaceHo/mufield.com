import pytz
from rest_framework import serializers
from rest_framework.fields import FileField
from musicfield import settings


class DateTimeTzSerializer(serializers.Serializer):
    def to_native(self, value):
        localize = pytz.timezone(settings.TIME_ZONE).localize(value)
        return str(localize)


class NullHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):
    '''
    for underlying absolute url representation, no url lookups :)
    '''

    def get_url(self, obj, view_name, request, format):
        return self.reverse(view_name, kwargs={}, request=request, format=format)

    def get_object(self, view_name, view_args, view_kwargs):
        pk = view_kwargs['pk']
        return self.get_queryset().get(pk=pk)


class CustomFileField(FileField):
    """
    Customized version of Django rest framework's ImageField that returns the
    absolute url property as opposed to the relative path to the media root
    """

    def to_representation(self, value):
        if value:
            return value.url
        else:
            return None


class ObjectHyperLinkedIdentityField(serializers.HyperlinkedIdentityField):
    def get_url(self, obj, view_name, request, format):
        """
        Given an object, return the URL that hyperlinks to the object.

        May raise a `NoReverseMatch` if the `view_name` and `lookup_field`
        attributes are not configured to correctly match the URL conf.
        """
        # Unsaved objects will not yet have a valid URL.
        if obj.pk is None:
            return None

        lookup_value = getattr(obj, self.lookup_field)

        import numbers
        from django.utils import six

        if lookup_value is not None and not isinstance(lookup_value, six.string_types) and not isinstance(lookup_value,
                                                                                                          numbers.Number):
            try:
                lookup_value = getattr(lookup_value, self.lookup_url_kwarg)
            except Exception as e:
                lookup_value = getattr(lookup_value, 'pk')

        if lookup_value is None or (not isinstance(lookup_value, six.string_types) and not isinstance(lookup_value,
                                                                                                      numbers.Number)) or '' == lookup_value:
            return None

        kwargs = {self.lookup_url_kwarg: lookup_value}
        return self.reverse(view_name, kwargs=kwargs, request=request, format=format)
