"""
Object level permissions
"""

from rest_framework import permissions

UPDATE_METHODS = ['PUT', 'PATCH']


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow objects be visible to anyone, but only allow 
    owners of an object to edit (i.e. update/delete) it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request, so we'll always allow
        # GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # if the group has no user then allow the first user to attempt updating
        # it to be the owner
        if not obj.owner and request.method in UPDATE_METHODS:
            return True

        # If here then there's an owner of the group.
        # Write permissions are only allowed to the owner of the group.
        return obj.owner == request.user
