from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsQuizOwner(BasePermission):
    """
    Custom permission to only allow owners of a quiz to edit or delete it.
    Assumes the model instance has an `owner` attribute.
    """
    message = "Only the quiz owner may edit or delete this quiz."

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user