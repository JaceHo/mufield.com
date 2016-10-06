from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

from apps.api.models import Group
from apps.join.views import e404
from apps.chat.utils import ChatPage
from apps.chat.forms import ChatTypeForm


@csrf_exempt
def chat(request, chat_token):
    if not Group.validate_chat_token(chat_token):
        return e404(request, template_name='404.html')

    chat = Group.objects.get_all_by_token(chat_token)
    if chat.status == Group.STATUS_CLOSED:
        return redirect('/')

    chat_page = ChatPage(request)
    c = {'user_token': chat_page.get_user_token(), 'chat_status': chat.status, 'form': ChatTypeForm()}
    return render_to_response('chat.html', c, context_instance=RequestContext(request))
