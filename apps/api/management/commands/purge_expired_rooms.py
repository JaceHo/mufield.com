"""
Description:
  Manangement command module for purging the database of expired groups
  
Author: 
   
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from django.utils import timezone

from apps.api.models import Group


class Command(BaseCommand):
    help = 'Delete all expired groups'

    def handle(self, *args, **options):
        """
        Delete all expired groups and rebuild the search index when done.
        
        Arguments:   *args, **options
        Return:      None
        """
        # get all expired groups
        earliest_date = timezone.now() - timedelta(
            seconds=settings.GROUP_EXPIRY_TIME_SECONDS)
        expired_groups = Group.objects.all().filter(ctime__lt=earliest_date)

        # delete the expired groups by calling each object's delete() method
        # as we want all appropriate cleanup to be done.
        for group in expired_groups:
            group.delete()

        # rebuild the index (quietly)
        call_command('rebuild_index', interactive=False, verbosity=0)
        
