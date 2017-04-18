from rest_framework import permissions


class IsOwnerOrReadOnly():
    """
    Custom permission to only allow owners to edit an object
    """

    def has_object_permission(self, request, obj):
        # Read permissions are allowed to any request,
        # so always allow GET/HEAD/OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write/update are only allowed to the owner of the object
        return obj.user == request.user
