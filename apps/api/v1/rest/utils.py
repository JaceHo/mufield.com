# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import time
from datetime import datetime
import os
import re
import unicodedata
from rest_framework import status
from rest_framework.response import Response

from rest_framework.views import exception_handler
from unidecode import unidecode

from musicfield import settings

REPLACE1_REXP = re.compile(r'[\']+')
REPLACE2_REXP = re.compile(r'[^-a-z0-9]+')
REMOVE_REXP = re.compile('-{2,}')


def get_upload_path(instance, filename, root):
    """
    Description: Determine a unique upload path for a given file

    Arguments:   - instance: model instance where the file is being attached
                 - filename: filename that was originally given to the file
                 - root:     root folder to be prepended to file upload path.
                             Example value is 'photo/' or 'photo'
    Return:      Unique filepath for given file, that's a subpath of `root`
    """
    name = smart_truncate(filename).split('.')
    format = slugify('.'.join(name[:-1])) + '_' + str(datetime.now().strftime("%Y%m%dT%H%M%S")) + '.' + name[-1]
    return os.path.join(root, format)


def custom_exception_handler(exc):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    from apps.api.middlewares import get_current_request

    response = exception_handler(exc, get_current_request())

    # Now add the HTTP status code for the response.
    if response is not None:
        if isinstance(response.data, (list, dict)) and len(response.data) == 1 and response.data.get('detail'):
            response.data = {'results': {'code': response.status_code, 'msg': response.data.get('detail')}}
        else:
            response.data = {'results': {'code': response.status_code, 'msg': response.data}}
    else:
        if not settings.DEBUG:
            # for production, always return json response
            response = Response(
                data={
                    'results': {
                        'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                        'msg': 'If problem persist, please contact the administrator'
                    }
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            # return none for response will raise an exception here

    if response:
        print(response.status_code, response.status_text, response.data)
    return response


class LongPolling:
    @staticmethod
    def run(chat, user_token):
        """
        Run long polling
        :param chat: Chats
        :param user_token: String
        :return Chats
        """
        sleep = settings.MUFIELD_API['long_polling']['sleep']
        iteration = settings.MUFIELD_API['long_polling']['iteration']
        auto_close = 2 * sleep * iteration
        chat_token = str(chat.id)

        # init long polling process and terminate all old ones
        init_polling_id = chat.create_long_polling(user_token)
        actual_polling_id = init_polling_id

        # run long polling
        i = 1
        from apps.api.models import Group

        while i < iteration \
                and chat.count == 0 \
                and chat.status != Group.STATUS_CLOSED \
                and init_polling_id == actual_polling_id:
            time.sleep(sleep)
            chat = Group.get_chat(chat_token, user_token)
            long_polling = chat.get_long_polling(user_token)
            actual_polling_id = str(long_polling._id) if long_polling else False
            i += 1

        # close automatically chat if talker close browser or tab
        chat.auto_close_long_polling(user_token, auto_close)

        return Group.get_chat(chat_token, user_token)


def list_dedup(in_list):
    """
    Description: Dedup a list and preserve order

    Arguments:   - in_list: list to have its duplicates removed
    Return:      Dedup'd version of passed list

    Author:       
    """
    seen = set()
    return [s for s in in_list if s not in seen and not seen.add(s)]


def get_request_ip(request):
    if request.META.get('HTTP_X_FORWARDED_FOR', None):
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']
    return ip


def human_readable_size(num):
    """
    Description: Present a human readable size size from bytes.
    >>> human_readable_size(2048)
    '2 bytes'

    Arguments:
    - num: number of bytes to be converted

    Return:
    - A string that represents a human readable size

    Ref: http://stackoverflow.com/a/1094933
    """
    for x in ['bytes', 'KB', 'MB', 'GB']:
        if 1024.0 > num > -1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
    return "%3.1f %s" % (num, 'TB')


def permission_denied_handler(request):
    from django.contrib.auth import views

    return views.login(request, template_name='rest_framework/login.html')


def smart_truncate(string, max_length=0, word_boundaries=False, separator=' '):
    """ Truncate a string """

    string = string.strip(separator)

    if not max_length:
        return string

    if len(string) < max_length:
        return string

    if not word_boundaries:
        return string[:max_length].strip(separator)

    if separator not in string:
        return string[:max_length]

    truncated = ''
    for word in string.split(separator):
        if word:
            next_len = len(truncated) + len(word) + len(separator)
            if next_len <= max_length:
                truncated += '{0}{1}'.format(word, separator)
    if not truncated:
        truncated = string[:max_length]
    return truncated.strip(separator)


def slugify(text, max_length=0, word_boundary=False, separator='-'):
    """ Make a slug from the given text """

    # decode unicode ( 影師嗎 = Ying Shi Ma)
    text = unidecode(text)

    # translate
    text = unicodedata.normalize('NFKD', text)

    # replace unwanted characters
    text = REPLACE1_REXP.sub('', text.lower())  # replace ' with nothing instead with -
    text = REPLACE2_REXP.sub('-', text.lower())

    # remove redundant -
    text = REMOVE_REXP.sub('-', text).strip('-')

    # smart truncate if requested
    if max_length > 0:
        text = smart_truncate(text, max_length, word_boundary, '-')

    if separator != '-':
        text = text.replace('-', separator)

    return text
