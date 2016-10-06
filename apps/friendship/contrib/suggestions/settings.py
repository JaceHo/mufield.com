from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
try:
    from django.utils.importlib import import_module
except ImportError:
    from importlib import import_module


def map_to_attr(setting, default=None):
    if default is None:
        try:
            path = getattr(settings, setting)
        except AttributeError:
            raise ImproperlyConfigured("You must define '%s' in settings" % setting)
    else:
        path = getattr(settings, setting, default)
    i = path.rfind(".")
    module, attr = path[:i], path[i + 1:]
    try:
        mod = import_module(module)
    except ImportError as e:
        raise ImproperlyConfigured("Error importing %s: '%s'" % (module, e))
    try:
        attr = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured("Module '%s' does not define a '%s'" % (module, attr))
    return attr


RUNNER = map_to_attr(
    "FRIENDS_SUGGESTIONS_IMPORT_RUNNER",
    "friendship.contrib.suggestions.backends.runners.SynchronousRunner"
)
