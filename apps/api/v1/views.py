from rest_framework import parsers
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken import views
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import renderers

from rest_framework.views import APIView

from apps.api.models import User
from apps.api.v1.account.serializers import TokenSerializer
from apps.api.v1.rest import generics as custom_generics


@api_view(('GET',))
def api_root(request, format=None):
    '''
    Index top level api endpoints(REST API , ICECAST2 STREAMING API, MQTT STREAMING API ARE INCLUDED)

    #The ICECAST2  API (port 8989)
    ## More about icecast2 protocol is avaliable here
    [icecast2 protocol reference](`https://www.indexcom.com/streaming/player/Icecast2.html`)
    ### client server socket negotiation
    ##client  data < 8192 bytes
    ###client  data format also ended with \\r\\n\\r\\n
        icy-metadata: enabled\\r\\n
        icy-streaming-suffix:media/00/01.mp3 \\r\\n
        icy-streaming-offset-time: 0 \\r\\n
        \\r\\n

    ###server response with
        def _write_header(self, sock, str):
            sock.send(str + '\\r\\n')
        self._write_header(client.sock, 'ICY 200 OK')
        self._write_header(client.sock, 'icy-name:OCXRadio. OverClocked ReMix Radio.')
        self._write_header(client.sock, 'icy-genre:Video Game.')
        self._write_header(client.sock, 'icy-url:http://www.mufield.com/mufieldradio/')
        self._write_header(client.sock, 'content-type:audio/mpeg')
        self._write_header(client.sock, 'icy-pub:0')

        if client.supportsmetadata: ( from icy-metadata : enabled|disabled )
            self._write_header(client.sock, 'icy-metaint:%d' % (MP3Chunker.ChunkSize))

        self._write_header(client.sock, 'icy-br:%d' % (g_mp3chunker.bitrate))
    ###And begin with streaming mp3

    # The MQTT STREAMING API:
    *For subscribing*

        mufield.com:1883 //for password auth
        mufield.com:8883 //for tls(https) auth

    ## Reading
    You can read using this endpoint. While it would seem nice for this API
    endpoint to stream all feedbacks you can imagine why this is .

    ### Fields
    If reading this endpoint returned a list of user objects, each user object
    would only contains public user data.

     Topic              | Description                          | Fields
    ------------------ | ---------------------------------- | ----------
    `mufield/sys/musics/new` | new music feeds each day | ref */musics/<id>*
    `mufield/users/[clientId]/others/[otherId]/chats/request`| receive others friend request in a chat|ref /user/chats/<id>/messages/<id>, hyperlink now as talkerId
    `mufield/users/[clientId]/friends/[friendId]/chats/message`| receive friends chats| same as above
    `mufield/users/[chientId]/groups/[groupId]/chats/message` |recieve groups chats| same as above
    `mufield/users/[clientId]/friends/[friendId]/posts/new`|recieve friends new post notify |
    `mufield/users/[clientId]/friends/[friendId]/posts/comment`|
    `mufield/users/[clientId]/friends/[friendId]/posts/like`|

    ### Permissions
    * Anyone authenticated can using this endpoint.

    ###subscribing

    ####For client with Id `selfId`:
    `Subscribing` chat message, the topics will be:

        mufield/users/[selfId]/others/+/chats/request
        mufield/users/[selfId]/friends/+/chats/message
        mufield/users/[selfId]/groups/+/chats/message

    #The REST API:
    ## Note
    The default type
    `Fields` in fields table is of the format:

    Type |  Example value
    -----------------|-----------------
    `date/time` |"2015-02-11T07:13:20"
    `string` |"simple text"
    `integer` |10
    `url` |"https://api.mufield.com/cc.mp3"
    `choice` | 1 or "value2" or 3.14
    `file`   | [fileupload]
    `boolean`  | false or true
    `decimal` | 32.3322

    #
    _`result` object_ is of the format:

        {
            "results":
            {
                "code":  201,
                "msg": "ok"
            }
        }

    The default error message

        {
            "results":
            {
                "code":  403,
                "msg": "You do not have the permission to edit this"
            }
        }

    or field specified error msg:

        {
            "results":
            {
                "code":  404,
                "msg": {
                    "field1":"user with the id already exists!"
                    "field2":"wrong name!!!!"
                    "field3":"wrong city!!!!"
                    "field4":"wrong coutry!!!!"
                }
            }
        }

    The default list of object
    #
    _`list` object_ is of the format:

        {
            "count":23,
            "next":"https://api.mufield.com/v1/blob",
            "previous":"https://api.mufield.com/v1/blob",
            "results":
            [
                ```[The object type]```
            ]
        }
    #

    '''

    return Response({
        'token': reverse('v1:token', request=request, format=format),
        'authenticated user': reverse('v1:user-auth-detail', request=request,
                                      format=format),
        'users': reverse('v1:user-list', request=request, format=format),
        'users-sms': reverse('v1:users-sms', request=request, format=format),
        'user-music-cloud': reverse('v1:user-music-list', request=request, format=format),
        'artists': reverse('v1:artist-list', request=request, format=format),
        'musics': reverse('v1:music-list', request=request, format=format),
        'fieldnames': reverse('v1:fieldname-list', request=request, format=format),
        'groups': reverse('v1:group-list', request=request, format=format),
        'explore': reverse('v1:explore_root', request=request, format=format),
        'search': reverse('v1:search_root', request=request, format=format),
    })


class TokenView(views.ObtainAuthToken, custom_generics.RetrieveAPIView):
    '''
    Get access token by username and password, create it by `POST`, retrieve it by `GET`
    when post for token both p<phone_number> or n<username>  is valide for clients(<> is just a sign here)
    '''
    renderer_classes = (renderers.BrowsableAPIRenderer, renderers.JSONRenderer,)

    def post(self, request):
        u = request.data['username']
        if u[0] == 'p':
            name = User.objects.get(phone=u[1:]).username
            request.data['username'] = name
        elif u[0] == 'n':
            request.data['username'] = u[1:]
        return ObtainAuthToken.post(self, request)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AuthTokenSerializer
        else:
            return TokenSerializer

    def get_object(self):
        return Token.objects.get(user=self.request.user)


class ObtainAuthToken(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)

    def post(self, request):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'id': user.pk, 'username':user.username})


obtain_auth_token = ObtainAuthToken.as_view()
