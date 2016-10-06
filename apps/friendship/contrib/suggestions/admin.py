from django.contrib import admin

from apps.friendship.contrib.suggestions.models import FriendshipSuggestion, ImportedContact


class FriendshipSuggestionAdmin(admin.ModelAdmin):
    list_display = ["id", "from_user", "to_user", "added"]


class ImportedContactAdmin(admin.ModelAdmin):
    list_display = ["id", "owner", "name", "added"]


admin.site.register(FriendshipSuggestion, FriendshipSuggestionAdmin)
admin.site.register(ImportedContact, ImportedContactAdmin)
