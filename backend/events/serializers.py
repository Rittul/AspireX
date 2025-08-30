from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from .models import Event
from mentor.models import Mentor


class EventSerializer(serializers.ModelSerializer):
    organizer_type = serializers.SerializerMethodField()
    organizer_name = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'start_time', 'end_time', 'location', 'cover_image',
            'created_by_role', 'is_published', 'created_at', 'updated_at',
            'organizer_type', 'organizer_name',
        ]
        read_only_fields = ['created_by_role', 'created_at', 'updated_at', 'organizer_type', 'organizer_name']

    def get_organizer_type(self, obj):
        model = obj.organizer_content_type.model if obj.organizer_content_type else None
        if model == 'mentor':
            return 'mentor'
        return 'admin'

    def get_organizer_name(self, obj):
        organizer = getattr(obj, 'organizer', None)
        if organizer is None:
            return None
        # Mentor has name; Student(admin) likely has name
        return getattr(organizer, 'name', None) or getattr(organizer, 'email', None)

    def validate(self, attrs):
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')

        # Normalize empty end_time
        if end_time in ('', None):
            attrs['end_time'] = None
            end_time = None

        if start_time and timezone.is_naive(start_time):
            attrs['start_time'] = timezone.make_aware(start_time)
        if end_time and timezone.is_naive(end_time):
            attrs['end_time'] = timezone.make_aware(end_time)
        if attrs.get('end_time') and attrs['end_time'] <= attrs['start_time']:
            raise serializers.ValidationError('End time must be after start time')
        return attrs

    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        if getattr(user, 'is_staff', False):
            # Admin via Student model (AUTH_USER_MODEL)
            content_type = ContentType.objects.get_for_model(user.__class__)
            created_by_role = 'admin'
        elif isinstance(user, Mentor):
            content_type = ContentType.objects.get_for_model(Mentor)
            created_by_role = 'mentor'
        else:
            raise serializers.ValidationError('Only mentors or admins can create events')

        event = Event.objects.create(
            organizer_content_type=content_type,
            organizer_object_id=user.pk,
            created_by_role=created_by_role,
            **validated_data,
        )
        return event

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance 