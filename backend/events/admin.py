from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'location', 'created_by_role', 'is_published')
    list_filter = ('created_by_role', 'is_published', 'start_time')
    search_fields = ('title', 'description', 'location')
    ordering = ('start_time',) 