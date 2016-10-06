from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken import views
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import renderers
from apps.api.v1.account.serializers import TokenSerializer
from apps.api.v1.rest import generics as custom_generics


@api_view(('GET',))
def api_root(request, format=None):
    '''
    Index top level api endpoints

    # The STREAMING API:
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
    The default error message
    #
    _`result` object_ is of the format:

        {
            'results':
            {
                "code":  403,
                "msg": 'You do not have the permission to edit this'
            }
        }



    '''

    return Response({
        'token': reverse('v1:token', request=request, format=format),
    })

