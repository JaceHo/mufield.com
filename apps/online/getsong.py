#!/usr/bin/python
# -*- coding:utf-8 -*-
from urllib import request, parse

from xml.etree import ElementTree as XmlTree
import os

DOWNLOAD_URL = 'http://box.zhangmen.baidu.com/x?op=12&count=1&title={}$${}$$$$'
LRC_URL = 'http://box.zhangmen.baidu.com/bdlrc/{}/{}.lrc'


def get_music_url(music_name, author_name):
    if author_name is None:
        author_name = ''
    link = DOWNLOAD_URL.format(parse.quote_plus(music_name.encode().decode()),
                               parse.quote_plus(author_name.encode().decode()))
    response = request.urlopen(link)  # 返回一个文件类型的对象

    xml = response.read()
    response.close()

    '''转换编码格式'''
    xml = xml.decode('gb2312').encode('utf-8').decode()
    xml = xml.replace('encoding="gb2312"', 'encoding="UTF-8"')

    try:
        root = XmlTree.fromstring(xml)  # 加载xml字符串
        # If this line enabled, will download lower quality mp3
        # url  = root.find('url')
        # If this line enabled, will download higher quality mp3
        url = root.find('durl')
        encd = url.find('encode')
        decd = url.find('decode')
        lrcid = url.find('lrcid').text
        addr = encd.text
        exts = decd.text
        base = addr[:addr.rfind('/')]
        full = os.path.join(base, exts)  # 拼接，取得歌曲真正的下载地址
        lrc = LRC_URL.format(str(int(int(lrcid) / 100)), lrcid)  # 歌词下载
        return full + '|' + lrc
    except Exception as e:
        print('Exception:', e)
        print('>>>Music name is not matched with author name')
        return None

