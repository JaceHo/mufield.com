#! /usr/bin/env python
# -*- coding: utf-8 -*-
import urllib3
import json
from urllib import parse

"""\
user 163 music server to fetch audio info and lrc download address
"""


class MusicsearchAPI():
    def __init__(self):
        self.http = urllib3.PoolManager()
        self.sysencode = "utf-8"  # sys.getdefaultencoding()
        self.PluginName = "网易云音乐搜索插件"
        self.PluginAuthor = "BBDXF"
        self.PluginVersion = "1.0.0"
        self.audioinfo = {
            "songid": "",
            "title": "",
            "artist": "",
            "album": "",
            "duration": "",
            "audiourl": "",
            "lrcurl": "",
            "picurl": "",
        }
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": "appver=2.0.2",
            "Referer": "http://music.163.com",
        }

    """
    def __encrypted_id(self, id):
        byte1 = bytearray('3go8&$8*3*3h0k(2)2')
        byte2 = bytearray(id)
        byte1_len = len(byte1)
        for i in xrange(len(byte2)):
            byte2[i] = byte2[i]^byte1[i%byte1_len]
        m = md5.new()
        m.update(byte2)
        result = m.digest().encode('base64')[:-1]
        result = result.replace('/', '_')
        result = result.replace('+', '-')
        return result
    """

    def __searchdownloadurl(self):
        detail_url = 'http://music.163.com/api/song/detail/?id={0}&ids=[{0}]'.format(self.audioinfo['songid'])
        resp = self.http.request('POST', detail_url, headers=self.headers)
        detail_js = json.loads(resp.data.decode())
        if detail_js is not None and detail_js['code'] == 200:
            self.audioinfo['duration'] = int(detail_js['songs'][0]['duration']) // 1000
            self.audioinfo['audiourl'] = detail_js['songs'][0]['mp3Url']
            self.audioinfo['picurl'] = detail_js['songs'][0]['album']['blurPicUrl']
            self.audioinfo['lrcurl'] = "http://music.163.com/api/song/media?id={0}&version=0&csrf_token=" \
                .format(self.audioinfo['songid'])  # { lyric : "歌词内容用\n分割" , code: 200}

    def searchaduioinfo(self, **kwargs):
        '''
        SearchAduioInfo(**kwargs):
        :keyword title = 歌曲名 [, artist = 歌唱者 , album = 专辑]
        curl -d "s=小苹果&type=1&offset=0&sub=false&limit=6" "http://music.163.com/api/search/get/web?csrf_token="  -H "Cookie: appver=2.0.2" -H  "Referer: http://music.163.com/"
         '''
        title = kwargs.get("title", None)
        if title is None:
            return None
        search_url = "http://music.163.com/api/search/get/web?csrf_token="
        params = {
            's': title,
            'type': 1,  # 10 专辑， 1006 歌词, 100 歌手， 1000 歌单, 1002 用户
            'offset': 0,
            'sub': 'false',
            'limit': 6
        }
        print(parse.urlencode(params))
        resp = self.http.urlopen('POST', search_url, headers=self.headers, body=parse.urlencode(params))
        resp_js = json.loads(resp.data.decode())
        if resp_js['code'] == 200 and resp_js['result']['songCount'] > 0:
            result = resp_js['result']
            if result['songCount'] > 0:
                # print type(result['songs'][0]['name'])
                self.audioinfo['songid'] = result['songs'][0]['id']
                self.audioinfo['title'] = result['songs'][0]['name']
                self.audioinfo['artist'] = result['songs'][0]['artists'][0]['name']
                self.audioinfo['album'] = result['songs'][0]['album']['name']
                for i in range(len(result['songs']) - 1, -1, -1):
                    song = result['songs'][i]
                    # print '[%2d]song:%s\tartist:%s\talbum:%s\t %s' % (i+1,song['name'], song['artists'][0]['name'], song['album']['name'], song['id'])
                    if kwargs['title'] == song['name'].encode(self.sysencode):
                        self.audioinfo['title'] = song['name']
                        self.audioinfo['songid'] = song['id']
                        self.audioinfo['artist'] = song['artists'][0]['name']
                        self.audioinfo['album'] = song['album']['name']
                        if kwargs.get('artist') is not None:
                            if song['artists'][0]['name'].encode(self.sysencode) == kwargs.get('artist'):
                                self.audioinfo['title'] = song['name']
                                self.audioinfo['songid'] = song['id']
                                self.audioinfo['artist'] = song['artists'][0]['name']
                                self.audioinfo['album'] = song['album']['name']
                                if kwargs.get('album') is not None:
                                    if song['album']['name'].encode(self.sysencode) == kwargs.get('album'):
                                        self.audioinfo['title'] = song['name']
                                        self.audioinfo['songid'] = song['id']
                                        self.audioinfo['artist'] = song['artists'][0]['name']
                                        self.audioinfo['album'] = song['album']['name']
                                        break
                                else:
                                    break
                        else:
                            break
                # 查询下载地址和歌词地址等
                self.__searchdownloadurl()
                return 1
        return 0


def convert(input):
    if isinstance(input, dict):
        return {convert(key): convert(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [convert(element) for element in input]
    else:
        return input.encode('utf-8')


def test():
    p = MusicsearchAPI()
    """
    song_id = 190072
    detail_url = 'http://music.163.com/api/song/detail/?id={0}&ids=[{0}]'.format(song_id)
    resp = urllib3.urlopen(detail_url)
    song_js = json.loads(resp.read())
    rest = song_js['songs'][0]
    print convert(rest)
    return None
    """
    p.postLrc()
    # p.searchaduioinfo(title="黄昏")
    # for k, v in p.audioinfo.items():
    #    print k, "=", v


if __name__ == "__main__": test()
