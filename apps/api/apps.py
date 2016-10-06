from django.apps import AppConfig

from musicfield.settings import MP3_STREAM


class ApiConfig(AppConfig):
    name = 'apps.api'
    verbose_name = "api app"
    label = 'api'

    def ready(self):

        import socket

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', MP3_STREAM['port']))
        if result == 0:
            print("Port is open")
        else:
            print("Port is not open")
            from apps.api.v1.music import stream_server

            stream_server.start_stream()

        from apps.api.services import acl_sync


        from apps.api.services import SyncService

        SyncService()
