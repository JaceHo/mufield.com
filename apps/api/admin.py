from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import forms

from apps.api.models import Music, Group, Feed, Artist, Field, FieldName, GroupShip, Torrent, MusicUser
from apps.api.models import User
from apps.api.v1.feedback.forms import FeedbackForm
from django.contrib import admin
from django.conf import settings
from django import forms
from apps.api.models import Music, Album, Artist


def delete_selected_s(modeladmin, request, queryset):
    """
    Description: A version of the "deleted selected objects" action which calls
                 the Music model's `delete()` method. This is needed because the
                 default version uses `QuerySet.delete()`, which doesn't call
                 the model's `delete()` method.

    Arguments:   - modeladmin: The Music ModelAdmin
                 - request:    HttpRequest object representing current request
                 - queryset:   QuerySet of set of Music objects selected by user.
    Return:      None

    Author:      Nnoduka Eruchalu
    """
    for obj in queryset:
        obj.delete()


delete_selected_s.short_description = "Delete selected songs"


def delete_selected_a(modeladmin, request, queryset):
    """
    Description: A version of the "deleted selected objects" action which calls
                 the Album model's `delete()` method. This is needed because the
                 default version uses `QuerySet.delete()`, which doesn't call
                 the model's `delete()` method.

    Arguments:   - modeladmin: The Album ModelAdmin
                 - request:    HttpRequest object representing current request
                 - queryset:   QuerySet of set of Album objects selected by user
    Return:      None

    Author:      Nnoduka Eruchalu
    """
    for obj in queryset:
        obj.delete()


delete_selected_a.short_description = "Delete selected albums"


class MusicAdminForm(forms.ModelForm):
    """
    Description: Custom form to be used with Music's ModelAdmin, MusicAdmin.
                 The purpose is to override the default admin form behavior
                 by adding more validations to uploaded mp3 file.

    Functions:   - clean_mp3: validate uploaded file size and type

    Author:      Nnoduka Eruchalu
    """

    def clean_mp3(self):
        """
        Description: Ensure uploaded mp3 file is within allowed limits and is
                     of the right content type/mime type.

        Arguments:   None
        Return:      cleaned 'mp3' field data.

        Author:      Nnoduka Eruchalu
        """
        afile = self.cleaned_data.get('mp3', False)
        if afile:
            if afile.size > settings.MAX_AUDIO_SIZE:
                raise forms.ValidationError("audio file too large ( > %s bytes)"
                                            % settings.MAX_AUDIO_SIZE)
            if hasattr(afile, 'content_type') and \
                    (afile.content_type not in settings.AUDIO_FORMATS):
                raise forms.ValidationError(
                    "Upload a valid mp3 file. Detected file type: "
                    + afile.content_type)
            return afile
        else:
            raise forms.ValidationError("couldn't read uploaded audio file")


class MusicAdmin(admin.ModelAdmin):
    """
    Description: Representation of the Music model in the admin interface.

    Functions:   - get_actions: disable some actions for this ModelAdmin

    Author:      Nnoduka Eruchalu
    """

    actions = [delete_selected_s]
    readonly_fields = ('num_plays', 'duration')
    list_display = ('title', 'artist', 'album', 'num_plays',)
    search_fields = ('title', 'artist__name', 'album__title')
    ordering = ('title',)
    form = MusicAdminForm

    def get_actions(self, request):
        """
        Description: Permanently disable the default "deleted selected objects"
                     action for this ModelAdmin

        Arguments:   - request: HttpRequest object representing current request
        Return:      Updated list of actions.

        Author:      Nnoduka Eruchalu
        """
        actions = super(MusicAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


class AlbumAdmin(admin.ModelAdmin):
    """
    Description: Representation of the Album model in the admin interface.

    Functions:   - get_actions: disable some actions for this ModelAdmin

    Author:      Nnoduka Eruchalu
    """

    actions = [delete_selected_a]
    search_fields = ('title',)
    list_display = ('title',)

    def get_actions(self, request):
        """
        Description: Permanently disable the default "deleted selected objects"
                     action for this ModelAdmin

        Arguments:   - request: HttpRequest object representing current request
        Return:      Updated list of actions.

        Author:      Nnoduka Eruchalu
        """
        actions = super(AlbumAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        return False


class ArtistAdmin(admin.ModelAdmin):
    """
    Description: Representation of the Artist model in the admin interface.

    Author:      Nnoduka Eruchalu
    """
    search_fields = ('name',)
    list_display = ('name',)


# Register your admin here.



class GroupAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        obj.save()


def delete_selected_a(modeladmin, request, queryset):
    """
    A version of the "deleted selected objects" action which calls the model's
    `delete()` method. This is needed because the default version uses
    `QuerySet.delete()`, which doesn't call the model's `delete()` method.

    Arguments:
      - modeladmin: The AuthToken ModelAdmin
      - request:    HttpRequest object representing current request
      - queryset:   QuerySet of set of Group objects selected by admin

    Return:
      None
    """
    for obj in queryset:
        obj.delete()


def delete_selected_u(modeladmin, request, queryset):
    """
    A version of the "deleted selected objects" action which calls the model's
    `delete()` method. This is needed because the default version uses
    `QuerySet.delete()`, which doesn't call the model's `delete()` method.

    Arguments:
      - modeladmin: The Group ModelAdmin
      - request:    HttpRequest object representing current request
      - queryset:   QuerySet of set of Group objects selected by admin

    Return:
      None
    """
    for obj in queryset:
        obj.delete()


delete_selected_u.short_description = "Delete selected user(s)"


class FeedbackAdmin(admin.ModelAdmin):
    """
    Representation of Feedback model in admin interface with a custom form
    """
    form = FeedbackForm


class MyUserCreationForm(UserCreationForm):
    """
    emqttd's version of the user creation form which update's the metadata
    specifying associated model to the customer User model.

    Also overrides clean_phone which directly references the built-in User
    model
    """
    phone = forms.RegexField(regex=r'^\+?1?\d{9,15}$',
                             error_message=(
                                 "Phone number must be entered in the format: '+18012345678'. Up to 15 digits allowed."))

    def clean_phone(self):
        # Since User.phone is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        phone = self.cleaned_data['phone']
        try:
            User.objects.get(phone=phone)
        except User.DoesNotExist:
            return phone
        raise forms.ValidationError(
            self.error_messages['duplicate_phone'],
            code='duplicate_phone',
        )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", 'phone',)


class MyUserAdmin(UserAdmin):
    """
    mufield's version of the ModelAdmin associated with the User model. It is
    modified to work with the custom User model

    Functions:
      - get_actions: disable some actions for this ModelAdmin

    Author:

    """

    readonly_fields = ('last_login', 'date_joined', 'last_modified')
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'phone', 'password1', 'password2')}
         ),
    )

    # changing the displayed fields via `fieldsets` requires updating the form
    # customizing the User model requires changing the add form
    actions = [delete_selected_u]
    add_form = MyUserCreationForm
    list_display = ('username', 'first_name', 'email', 'date_joined',
                    'is_staff', 'latitude', 'longitude', 'geo_time',
                    'liked_artist', 'last_stayed_field', 'sex', 'moment')
    ordering = ('-date_joined',)

    fieldsets = (
        ('Personal info', {'fields': ('username', 'name', 'sex', 'avatar', 'phone', 'email', 'password')}),
        ('Personal status', {'fields': ('latitude', 'longitude', 'moment')}),
        ('Personal linked', {'fields': ('liked_artist', 'last_listened_song')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                    'groups', 'user_permissions',)}),
        ('Important time', {'fields': ('last_login', 'date_joined',
                                       'last_modified')}),
    )

    def get_actions(self, request):
        """
        Permanently disable the default "deleted selected objects" action for
        this ModelAdmin

        Arguments:
          - request: HttpRequest object representing current request
        Return:
          Updated list of actions.

        Author:

        """
        actions = super(MyUserAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


delete_selected_a.short_description = "Delete selected auth token(s)"

admin.site.register(Music, MusicAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Field)
admin.site.register(FieldName)
admin.site.register(GroupShip)
admin.site.register(Torrent)
admin.site.register(MusicUser)
admin.site.register(Group, GroupAdmin)
admin.site.register(Feed, FeedbackAdmin)
# Register UserAdmin
admin.site.register(User, MyUserAdmin)
