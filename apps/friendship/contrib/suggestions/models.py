import time

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from imagekit.models import ImageSpecField
from pilkit.processors import SmartResize
from pilkit.processors import Adjust

from apps.api.v1.fileio.fdfs_storage import FDFSStorage

from apps.friendship.contrib.suggestions.managers import FriendshipSuggestionManager

AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class FriendshipSuggestion(models.Model):
    """
    A friendship suggestion connects two users that can possibly know each other.
    Suggestions can be created by somehow comparing some of user profiles fields
    (like city or address) or by importing user contacts from external services
    and then comparing names and email of imported contacts with users.
    """

    from_user = models.ForeignKey(AUTH_USER_MODEL, verbose_name=_("from user"), related_name="suggestions_from")
    to_user = models.ForeignKey(AUTH_USER_MODEL, verbose_name=_("to user"), related_name="suggestions_to")
    added = models.DateTimeField(_("added"), default=timezone.datetime.utcnow())

    objects = FriendshipSuggestionManager()

    class Meta:
        unique_together = [("to_user", "from_user")]
        db_table = 'friendship_friendsuggestion'


class ImportedContact(models.Model):
    """
    Contact imported from external service.
    """
    # user who imported this contact
    owner = models.ForeignKey(AUTH_USER_MODEL, verbose_name=_("owner"), related_name="imported_contacts")
    ctime = models.IntegerField(max_length=20, default=int(time.time()))
    birth = models.DateField(blank=True, null=True, default=None, )
    signa = models.CharField(max_length=30, null=True, default=None)
    area = models.CharField(max_length=50, null=True, blank=True)
    career = models.CharField(max_length=30, null=True, blank=True)

    name = models.CharField(_("name"), max_length=100, null=True, blank=True)
    # Facebook does not give emails of user friends so email can be blank and
    # matching should be done using only name
    email = models.EmailField(_("email"), null=True, blank=True)
    sex = models.CharField(blank=False, default='F', choices=(('M', 'Male'), ('F', 'Female')), max_length=1,
                           help_text='F for female, M for male, default is F(female)')

    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+18012345678'. Up to 15 digits allowed.")
    phone = models.CharField(validators=[phone_regex], blank=True, max_length=16)  # validators should be a list
    # imagekit spec for avatar shown in mobile app's UITableViews
    avatar = models.ImageField(storage=FDFSStorage(), upload_to='img/avatar', verbose_name="Select Your Profile Image",
                               blank=True, null=True)
    avatar_thumbnail = ImageSpecField(
        source='avatar',
        processors=[SmartResize(width=120, height=120),
                    Adjust(contrast=1.2, sharpness=1.1)],
        format='JPEG',
        options={'quality': 90})

    added = models.DateTimeField(_("added"), default=timezone.datetime.utcnow())

    def save(self, *args, **kwargs):
        if self.__original_avatar and self.avatar != self.__original_avatar:
            # avatar has changed and this isn't the first avatar upload, so
            # delete old files.
            orig = ImportedContact.objects.get(pk=self.pk)
            self.delete_avatar_files(orig)

        # update the image file tracking properties
        self.__original_avatar = self.avatar
        if self.pk:
            u = ImportedContact.objects.get(pk=self.pk)
            if u.name != self.name or u.avatar != self.avatar or self.phone != u.phone or self.sex != u.sex or self.email != u.email or self.area != u.area or self.career != u.career or self.signa != u.signa or self.brith != u.brith:
                self.ctime = int(time.time())
        return super(ImportedContact, self).save(*args, **kwargs)

    def get_avatar_thumbnail_url(self):
        """
        get url of avatar's thumbnail. If there isn't an avatar_thumbnail then
        return an empty string
        """
        return self.avatar_thumbnail.url if self.avatar_thumbnail else ''

    def delete_avatar_files(self, instance):
        """
        Delete a user's avatar files in storage
        - First delete the user's ImageCacheFiles on storage. The reason this
          must happen first is that deleting source file deletes the associated
          ImageCacheFile references but not the actual ImageCacheFiles in
          storage.
        - Next delete source file (this also performs a delete on the storage
          backend)

        Arguments:
          - instance: User object instance to have files deleted
        Return:
          None

        Author:

        """
        # get avatar_thumbnail location and delete it
        instance.avatar_thumbnail.storage.delete(instance.avatar_thumbnail.name)
        # delete avatar
        instance.avatar.delete()

    @property
    def display_name(self):
        dname = ''
        if self.email:
            dname = self.email
        if dname and self.name:
            dname += " - "
        dname += self.name
        return dname

    def __unicode__(self):
        return _("%(display_name)s (%(owner)s's contact)") % {'display_name': self.display_name, 'owner': self.owner}

    class Meta:
        db_table = 'friendship_importedcontact'
