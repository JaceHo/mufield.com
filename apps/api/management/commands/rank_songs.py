"""
Description:
  Manangement command module for updating song trending rank/score for each 
  Song object in db
  
Author: 
  Nnoduka Eruchalu
"""

from django.core.management.base import BaseCommand, CommandError
from noddymix.apps.audio.models import Song, SongPlay, SongRank
from django.conf import settings
import datetime
from collections import Counter


class Command(BaseCommand):
    help = 'update all song rank scores'
    
    def handle(self, *args, **options):
        """
        Description: Clear all song ranks, get all songs played in the time
                     range used for heavy rotation and set their new scores.
                     The algorithm is somewhat based on the ranking performed by
                     Hacker News where each song played in the last 
                     `HEAVY_ROTATION_DAYS` days is scored using the formula:
                     Score = (P)/(T+2)^G
                     where,
                       P = number of song plays of an item
                       T = time since last song play
                       G = Gravity
                     Reference: http://amix.dk/blog/post/19574
                                 
        Arguments:   *args, **options
        Return:      None
        
        Author:      Nnoduka Eruchalu
        """
        # clear all song ranks
        SongRank.objects.all().delete()
        
        # want to use same value of now() everywhere
        now = datetime.datetime.now() 
        
        # heavily rotated songs are those with top scores in the last few days
        start_date = now - datetime.timedelta(days=settings.HEAVY_ROTATION_DAYS)
    
        # get all songs played over the last few days, with their play counts
        songplays = SongPlay.objects.filter(date_added__gte=start_date)
        
        # populate dictionary where keys are Song objects and values are 
        # 2-element lists of play count and hours since last play
        songs_playcnt_playtime = {}
        for songplay in songplays:
            song = songplay.song
            # if song not already in dictionary then this is most recent play
            # time and first acknowledged play.
            if song not in songs_playcnt_playtime:
                # remember we actually want time since last play in hours
                time_since_play = now - songplay.date_added
                time_since_play = time_since_play.seconds/3600.0
                songs_playcnt_playtime[song] = [1, time_since_play]
            
            # else song is already in dictionary, so account for one extra play
            else:
                songs_playcnt_playtime[song][0] += 1
        
        # create SongRank objects using appropriate scores
        for k, v in songs_playcnt_playtime.items():
            rank = v[0] / ((v[1] + 2.0)**settings.SONG_RANK_GRAVITY) 
            SongRank.objects.create(song=k, score=rank)
