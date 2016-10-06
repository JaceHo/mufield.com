"""
Description:
  Utility functions that come in handy for the app

Table Of Contents:
  - get_contacts:    get the contacts of any user

Author: 
   
"""


def get_contacts(user):
    """
    Get the contacts of any given User object. Note that this cannot be
    an anonymous user and this function won't check for that.
    
    We will find all users friendships utilizing the fact that they are 
    represented as 2-way relationships (i.e. 2 row entries in the DB).
    
    Arguments:   
      - user: User object of interest 
    Return:      
      List of User objects in user's contacts
    """
    # Observe the use of select_related. Here is an interesting post on using it
    # versus prefetch_related:
    # http://tech.yipit.com/2013/01/20/making-django-orm-queries-faster/
    friendships = Friendship.objects.filter(
        jid__istartswith=(user.username + '@')).select_related('username')
    return [friendship.username for friendship in friendships]
