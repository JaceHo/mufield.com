from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User


class FriendshipSuggestionManager(models.Manager):
    def suggested_friends_for_user(self, user):
        suggested_friends = []
        qs = self.filter(Q(from_user=user) | Q(to_user=user)).select_related(depth=1)
        for friendship_suggestion in qs:
            if friendship_suggestion.from_user == user:
                suggested_friends.append(friendship_suggestion.to_user)
            else:
                suggested_friends.append(friendship_suggestion.from_user)
        return suggested_friends

    def are_suggested_friends(self, user1, user2):
        return self.filter(
            Q(from_user=user1, to_user=user2) |
            Q(from_user=user2, to_user=user1)
        ).count() > 0

    def remove(self, user1, user2):
        friendship_suggestion = self.filter(from_user=user1, to_user=user2)
        if not friendship_suggestion:
            friendship_suggestion = self.filter(from_user=user2, to_user=user1)
        if friendship_suggestion:
            friendship_suggestion.delete()

    def create_suggestions_for_user_using_imported_contacts(self, user):
        """
        Creates friendship suggestions using contacts imported by user.
        """
        from friendship.contrib.suggestions.models import ImportedContact
        from friendship.models import Friend

        created = 0
        imported_contacts = ImportedContact.objects.filter(owner=user)
        for imported_contact in imported_contacts:
            suggested_friends = []
            # try to find matching user by phone number
            if imported_contact.phone:
                try:
                    suggested_friends.append(User.objects.get(phone=imported_contact.phone))
                except User.DoesNotExist:
                    pass
            # try to find matching user by email
            if imported_contact.email:
                try:
                    suggested_friends.append(User.objects.get(email=imported_contact.email))
                except User.DoesNotExist:
                    pass
            # if matching user not found by email try to match users by name 
            if not suggested_friends:
                try:
                    first_name, last_name = imported_contact.name.split(' ')
                    suggested_friends = User.objects.filter(first_name=first_name, last_name=last_name)
                except:
                    pass
            for suggested_friend in suggested_friends:
                if suggested_friend != user \
                        and not Friend.objects.are_friends(user, suggested_friend) \
                        and not self.are_suggested_friends(user, suggested_friend):
                    self.create(from_user=user, to_user=suggested_friend)
                    created += 1
        # we can also search other imported contacts using this user data
        imported_contacts = ImportedContact.objects.select_related('owner').filter(
            Q(email=user.email) | Q(name=user.first_name + ' ' + user.last_name))
        for imported_contact in imported_contacts:
            if imported_contact.owner != user \
                    and not Friend.objects.are_friends(user, imported_contact.owner) \
                    and not self.are_suggested_friends(user, imported_contact.owner):
                self.create(from_user=imported_contact.owner, to_user=user)
                created += 1
        return created
