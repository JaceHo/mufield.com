# Tunnel - TODO
#
# (C) 2010 Luke Slater, Steve 'Ashcrow' Milner
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Reaps sessions.
"""

import datetime
import logging

from django.core.management.base import NoArgsCommand
from django.contrib.sessions.models import Session
from django.conf import settings
from django.db import transaction

from tunnel.models import UserProfile


class Command(NoArgsCommand):
    """
    Reaps sessions that are no longer active.
    """

    help = "Can be run as a cronjob or directly to clean out expired sessions."

    def __init__(self, *args, **kwargs):
        """
        Creation of the reaper instance.

        :Parameters:
           - `args`: all non-keyword arguments
           - `kwargs`: all keyword arguments
        """
        NoArgsCommand.__init__(self, *args, **kwargs)
        logging.basicConfig(
            level=settings.TUNNEL_SESSION_REAPER_LOG_LEVEL,
            format='%(asctime)s %(levelname)s %(message)s',
            filename=settings.TUNNEL_SESSION_REAPER_LOG,
            filemode='a')
        logging.info('Session reaper running')

    def handle_noargs(self, **options):
        """
        How to reap sessions.

        :Parameters:
           - `options`: keyword arguments (which are ignored)
        """
        check_time = datetime.datetime.now() - datetime.timedelta(
            minutes=settings.TUNNEL_SESSION_REAPER_MINUTES_BETWEEN_CHECK)
        for profile in UserProfile.objects.filter(
            last_updated__lte=check_time):
            try:
                if profile.logged_in:
                    # TODO: Process reaping here
                    print(profile.user.username + ": is active")
            except:
                # User has now profile -- ignore them :-(
                pass
        # Same thing as cleanup command
        Session.objects.filter(
            expire_date__lt=datetime.datetime.now()).delete()
        transaction.commit_unless_managed()
