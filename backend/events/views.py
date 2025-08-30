from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from unified_auth.authentication import StudentOrMentorTokenAuthentication
from .models import Event
from .serializers import EventSerializer
from .permissions import IsMentorOrAdmin


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    authentication_classes = [StudentOrMentorTokenAuthentication]
    permission_classes = [IsMentorOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['start_time', 'created_at']
    ordering = ['start_time']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [perm() if isinstance(perm, type) else perm for perm in self.permission_classes]

    def get_queryset(self):
        qs = super().get_queryset().filter(is_published=True)
        include_past = self.request.query_params.get('include_past')
        organizer_me = self.request.query_params.get('organizer') == 'me'
        now = timezone.now()
        if not include_past:
            # Include upcoming or ongoing events
            qs = qs.filter(Q(start_time__gte=now) | Q(end_time__gte=now))
        if organizer_me and self.request.user and self.request.user.is_authenticated:
            from django.contrib.contenttypes.models import ContentType
            user = self.request.user
            content_type = ContentType.objects.get_for_model(user.__class__)
            qs = qs.filter(organizer_content_type=content_type, organizer_object_id=user.pk)
        return qs 