import datetime
from fdfs_client.client import Fdfs_client

__author__ = 'hippo'
# -*- coding:utf-8 -*-
import time

client_file = '../../../../config/etc/fdfs/client.conf'
test_file = 'upload.py'
download_file = 'upload.py'

import os

try:
    client = Fdfs_client(client_file)
    # upload
    ret_upload = client.upload_by_filename(test_file)
    # ret_upload = client.upload_by_buffer(b'buffer')
    #time.sleep(5)  # 等待5s，否则下载时会报错文件不存在
    file_id = ret_upload['Remote file_id']
    print(ret_upload['Remote file_id'])
    #print(os.system('curl  http://' + 'mufield.com/' + file_id))

    # download
    #ret_download = client.download_to_file(download_file, file_id)
    #print(ret_download)

    #print(client.set_meta_data(file_id, {'upload_time': round(time.mktime(datetime.datetime.now().timetuple()))}))
    #res = client.get_meta_data(file_id)
    # delete
    #ret_delete = client.delete_file(file_id)
    #print(ret_delete)

except Exception as ex:
    print(ex)
