import logging

from django.shortcuts import render_to_response
from django.template import RequestContext

logger = logging.getLogger(__name__)


def index(request):
    if request.user_agent.os.family == 'iOS':
        return render_to_response('mobile/index.html', {'ios': True}, context_instance=RequestContext(request))
    elif request.user_agent.os.family == 'Android':
        return render_to_response('mobile/index.html', {'ios': False}, context_instance=RequestContext(request))
    else:
        return render_to_response('index.html', {}, context_instance=RequestContext(request))
