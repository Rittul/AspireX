from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone


class Event(models.Model):
    ROLE_CHOICES = [
        ('mentor', 'Mentor'),
        ('admin', 'Admin'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    cover_image = models.URLField(max_length=1000, null=True, blank=True)

    organizer_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    organizer_object_id = models.PositiveIntegerField()
    organizer = GenericForeignKey('organizer_content_type', 'organizer_object_id')
    created_by_role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    is_published = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_time']
        indexes = [
            models.Index(fields=['start_time']),
            models.Index(fields=['is_published']),
        ]

    def __str__(self):
        return f"{self.title} @ {self.start_time.strftime('%Y-%m-%d %H:%M')}"

    @property
    def is_upcoming(self) -> bool:
        return self.start_time >= timezone.now() 