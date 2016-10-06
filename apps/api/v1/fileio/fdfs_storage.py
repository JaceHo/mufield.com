from io import BytesIO
import os
import time

from django.core.files import File
from django.core.files.storage import Storage
from django.utils.datetime_safe import datetime
from fdfs_client.client import Fdfs_client

from apps.api.v1.rest.mixins import Singleton
from musicfield import settings


class FDFSStorage(Singleton, Storage):
    """
    Standard fdfs filesystem storage
    """

    def __init__(self, client_config=None):
        self.client = Fdfs_client(client_config if client_config is not None else
                                  settings.PROJECT_PATH + '/config/etc/fdfs/client.conf'
                                  )

    def _open(self, name, mode='rb'):
        buffer = self.client.download_to_buffer(self.get_fileid(name))
        return File(BytesIO(buffer), mode)

    def _save(self, name, content):
        """
        @return dict {
            'Group name'      : group_name,
            'Remote file_id'  : remote_file_id,
            'Status'          : 'Upload successed.',
            'Local file name' : '',
            'Uploaded size'   : upload_size,
            'Storage IP'      : storage_ip
        } if success else None
        """

        print(content)
        dir_name, file_name = os.path.split(name)
        file_root, file_ext = os.path.splitext(file_name)
        try:
            # This file has a file path that we can upload.
            if hasattr(content, 'temporary_file_path'):
                res = self.client.upload_by_file(content.temporary_file_path(), file_ext)

            # This is a normal uploadedfile that we can stream.
            else:
                chunks = b''
                for chunk in content.chunks():
                    chunks += chunk
                res = self.client.upload_by_buffer(chunks, file_ext)
        except Exception as e:
            raise

        self.client.set_meta_data(res['Remote file_id'], {'size': res['Uploaded size'],
                                                          'name': res['Local file name'],
                                                          'created_time': round(
                                                              time.mktime(datetime.now().timetuple()))
                                                          })

        return '%s/%s?%s' % (res['Storage IP'], res['Remote file_id'], file_name) if res else None

    def delete(self, name):
        assert name, "The name argument is not allowed to be empty."
        try:
            self.client.delete_file(self.get_fileid(name))
        except Exception as ex:
            print(ex)

    def get_fileid(self, url):
        return '/'.join(url.split('?')[0].split('/')[1:])

    def exists(self, name):
        try:
            return self.client.get_meta_data(self.get_fileid(name)) is not None
        except:
            return False

    def listdir(self, path):
        return None

    def path(self, name):
        return name

    def size(self, name):
        meta = None
        try:
            meta = self.client.get_meta_data(self.get_fileid(name))
        except:
            pass
        return meta['size'] if meta else None

    def url(self, name):
        return name

    def accessed_time(self, name):
        return self.created_time(name)

    def created_time(self, name):
        meta = self.client.get_meta_data(self.get_fileid(name))
        return meta['created_time'] if meta else None

    def modified_time(self, name):
        return self.created_time(name)
