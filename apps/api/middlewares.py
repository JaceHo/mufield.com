import threading

from django.core.urlresolvers import resolve
from django.core.urlresolvers import reverse


class VersionSwitchMiddleware(object):
    def process_request(self, request):
        r = resolve(request.path_info)
        version = request.META.get('HTTP_X_MUFIELD_VERSION', False)
        if r.namespace.startswith('api:') and version:
            old_version = r.namespace.split(':')[-1]
            request.path_info = reverse('{}:{}'.format(r.namespace.replace(old_version, version), r.url_name),
                                        args=r.args, kwargs=r.kwargs)


_thread_locals = threading.local()


def get_current_request():
    return getattr(_thread_locals, 'request', None)


def get_current_user():
    return get_current_request().user


class ThreadLocalsMiddleware(object):
    """
    Middleware that gets various objects from the
    request object and saves them in thread local storage.
    """

    def process_request(self, request):
        _thread_locals.request = request
