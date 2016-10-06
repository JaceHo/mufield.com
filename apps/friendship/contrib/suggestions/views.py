from urllib.parse import urlencode
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required

from gdata.contacts.service import ContactsService

from apps.friendship.contrib.suggestions.backends.importers import GoogleImporter, FacebookImporter, TwitterImporter, YahooImporter, LinkedInImporter
from apps.friendship.contrib.suggestions.settings import RUNNER
from apps.friendship.contrib.suggestions.models import FriendshipSuggestion


@login_required
def suggested_friends(request, template_name="friendship/suggestions/suggested_friends.html"):
    """
    List suggested friends.
    """
    suggested_friends = FriendshipSuggestion.objects.suggested_friends_for_user(request.user)
    return render_to_response(template_name,
                              {"suggested_friends": suggested_friends},
                              context_instance=RequestContext(request))


def _import_status(request, results):
    """
    Check import task state and set appropriate messages.
    Returns True if import is finished, False otherwise.
    """
    if results.ready():
        if results.status == "SUCCESS":
            messages.success(request, _("%(total)s contacts found, %(imported)s new contacts imported, %(suggestions)s new friendship suggestions added.") % results.result)
        elif results.status == "FAILURE":
            messages.error(request, message=_("There was an error importing your contacts."))
        return True
    else:
        messages.info(request, _("We're still importing your contacts. It shouldn't take too long."))
        request.session["import_contacts_task_id"] = results.task_id
        return False


@login_required
def import_contacts(request,
                    template_name="friendship/suggestions/import_contacts.html",
                    extra_context=None):
    """
    If there is import_contacts_task_id in session pop it up and show info about
    this task using _import_status method.
    If there is no import_contacts_task_id in session check if there is 
    google_authsub_token, facebook_token, twitter_token, yahoo_token or
    linkedin_token in session and import contacts according to this token.
    """

    import_in_progress = False

    import_contacts_task_id = request.session.pop("import_contacts_task_id", None)
    if import_contacts_task_id:
        from celery.result import AsyncResult
        results = AsyncResult(import_contacts_task_id)
        import_in_progress = not _import_status(request, results)

    else:
        runner_class = RUNNER

        google_authsub_token = request.session.pop("google_authsub_token", None)
        if google_authsub_token:
            runner = runner_class(GoogleImporter,
                                  user=request.user,
                                  authsub_token=google_authsub_token)
            results = runner.import_contacts()
            import_in_progress = not _import_status(request, results)

        facebook_token = request.session.pop("facebook_token", None)
        if facebook_token:
            runner = runner_class(FacebookImporter,
                                  user=request.user,
                                  facebook_token=facebook_token)
            results = runner.import_contacts()
            import_in_progress = not _import_status(request, results)

        twitter_token = request.session.pop("twitter_token", None)
        if twitter_token:
            runner = runner_class(TwitterImporter,
                                  user=request.user,
                                  twitter_token=twitter_token)
            results = runner.import_contacts()
            import_in_progress = not _import_status(request, results)

        yahoo_token = request.session.pop("yahoo_token", None)
        if yahoo_token:
            runner = runner_class(YahooImporter,
                                  user=request.user,
                                  yahoo_token=yahoo_token)
            results = runner.import_contacts()
            import_in_progress = not _import_status(request, results)

        linkedin_token = request.session.pop("linkedin_token", None)
        if linkedin_token:
            runner = runner_class(LinkedInImporter,
                                  user=request.user,
                                  linkedin_token=linkedin_token)
            results = runner.import_contacts()
            import_in_progress = not _import_status(request, results)

    if not extra_context:
        extra_context = dict()
    extra_context['import_in_progress'] = import_in_progress
    return render_to_response(template_name,
                              extra_context,
                              context_instance=RequestContext(request))


def import_google_contacts(request, redirect_to=None):
    """
    If no token in GET params then redirect to Google page for granting permissions.
    If token is available, save it into session and redirect to import_contacts view. 
    """
    if redirect_to is None:
        redirect_to = reverse("friends_suggestions_import_contacts")
    if "token" in request.GET:
        request.session["google_authsub_token"] = request.GET["token"]
        return HttpResponseRedirect(redirect_to)
    authsub_url = ContactsService().GenerateAuthSubURL(next=request.build_absolute_uri(),
                                                       scope='http://www.google.com/m8/feeds/',
                                                       secure=False,
                                                       session=True)
    return HttpResponseRedirect(authsub_url)


@login_required
def import_facebook_contacts(request, access=None, auth_token=None):
    """
    If no auth_token is available redirect to Facebook page.
    If auth_token is availabe, save it into session and redirect to import_contacts view.
    """
    if auth_token:
        request.session["facebook_token"] = auth_token
        return HttpResponseRedirect(reverse("friends_suggestions_import_contacts"))
    else:
        return HttpResponseRedirect("%s?%s" % (
            reverse("oauth_access_login", args=["facebook", ]),
            urlencode({
                "next": request.build_absolute_uri()
            })
        ))


@login_required
def import_twitter_contacts(request, access=None, auth_token=None):
    """
    """
    if auth_token:
        request.session["twitter_token"] = auth_token
        return HttpResponseRedirect(reverse("friends_suggestions_import_contacts"))
    else:
        return HttpResponseRedirect("%s?%s" % (
            reverse("oauth_access_login", args=["twitter", ]),
            urlencode({
                "next": request.build_absolute_uri()
            })
        ))


@login_required
def import_yahoo_contacts(request, access=None, auth_token=None):
    """
    """
    if auth_token:
        request.session["yahoo_token"] = auth_token
        return HttpResponseRedirect(reverse("friends_suggestions_import_contacts"))
    else:
        return HttpResponseRedirect("%s?%s" % (
            reverse("oauth_access_login", args=["yahoo", ]),
            urlencode({
                "next": request.build_absolute_uri()
            })
        ))


@login_required
def import_linkedin_contacts(request, access=None, auth_token=None):
    """
    """
    if auth_token:
        request.session["linkedin_token"] = auth_token
        return HttpResponseRedirect(reverse("friends_suggestions_import_contacts"))
    else:
        return HttpResponseRedirect("%s?%s" % (
            reverse("oauth_access_login", args=["linkedin", ]),
            urlencode({
                "next": request.build_absolute_uri()
            })
        ))


