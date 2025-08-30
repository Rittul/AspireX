from rest_framework.permissions import BasePermission, SAFE_METHODS
from mentor.models import Mentor


class IsMentorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if getattr(user, 'is_staff', False):
            return True
        return isinstance(user, Mentor)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        if getattr(user, 'is_staff', False):
            return True
        # Mentor can edit/delete only their own events
        try:
            from django.contrib.contenttypes.models import ContentType
            from mentor.models import Mentor
            if isinstance(user, Mentor):
                return obj.organizer_object_id == user.pk and obj.organizer_content_type.model == 'mentor'
        except Exception:
            return False
        return False 