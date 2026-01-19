from rest_framework.permissions import BasePermission


class IsQuizOwner(BasePermission):
    """
    Custom permission to only allow owners of a quiz to edit or delete it.
    Assumes the model instance has an `owner` attribute.
    """
    message = "Only the quiz owner may edit or delete this quiz."

    def has_permission(self, request, view):
        """Allow authenticated users to access list view"""
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user