import threading

from django.template import RequestContext, Context, loader
from django.http import HttpResponse
from django.http import HttpResponseRedirect

from apps.api.models import Music, Artist, Album
from apps.api.v1.music.wangyiAPI import MusicsearchAPI
from .forms import MusicForm


# Create your views here.
def index(request):
    form = MusicForm()
    template = loader.get_template("online.html")
    order_list = Music.objects.filter(twisted=False)

    context = RequestContext(request, {
        'form': form,
        'order_list': order_list,
        'playing': 0,
    })
    return HttpResponse(template.render(context))


def response400():
    return HttpResponse(
        loader.get_template("find_nothing.html").render(Context({})))


def order(request):
    if request.method == 'POST':
        form = MusicForm(request.POST)
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
        if form.is_valid():
            p.searchaduioinfo(title=form.cleaned_data['title'].encode().decode(),
                              artist=form.cleaned_data['player'].encode().decode())
            for k, v in p.audioinfo.items():
                print(k, "=", v)
            new_order = Music.objects.get_or_create(
                artist=Artist.objects.get_or_create(name=form.cleaned_data['player'].encode().decode())[0],
                title=form.cleaned_data['title'].encode().decode())[0]
            dicts = p.audioinfo
            new_order.url = dicts['audiourl']
            new_order.lrc_url = dicts['lrcurl']
            Album.objects.get_or_create(title=dicts['album'], url=dicts['picurl'])
            new_order.album = Album.objects.get_or_create(title=dicts['album'])[0]
            new_order.duration = dicts['duration']
            if new_order.url is None or len(new_order.url) == 0 or new_order.lrc_url is None:
                return response400()
            threading.Thread(target=new_order.with_file_save).start()
            return HttpResponseRedirect("/online")
    else:
        return response400()
