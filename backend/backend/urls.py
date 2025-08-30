"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from student import views as student_views
from mentor import views as mentor_views
from chat import views as chat_views
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from student.models import Student
from mentor.models import Mentor, MentorDetail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import models

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from chat.models import NewsletterSubscriber
from chat.models import SiteStatus
router = DefaultRouter()

def aspirex_world(request):
    return HttpResponse('AspireX World')

def test_cors(request):
    return HttpResponse('CORS OK')

@csrf_exempt
def platform_stats(request):
    if request.method == 'GET':
        total_students = Student.objects.count()
        total_mentors = Mentor.objects.count()
        # Sum all sessions completed by all mentors
        total_sessions = MentorDetail.objects.aggregate(total=models.Sum('total_sessions'))['total'] or 0
        return JsonResponse({
            'total_students': total_students,
            'total_mentors': total_mentors,
            'total_sessions': total_sessions
        })
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def newsletter_subscribe(request):
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip()
            validate_email(email)
        except (json.JSONDecodeError, KeyError, ValidationError):
            return JsonResponse({'success': False, 'message': 'Invalid email.'}, status=400)
        # Save to DB if not already subscribed
        if NewsletterSubscriber.objects.filter(email=email).exists():
            return JsonResponse({'success': True, 'message': 'Already subscribed.'})
        NewsletterSubscriber.objects.create(email=email)
        return JsonResponse({'success': True, 'message': 'Subscribed successfully!'})
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def site_status(request):
    status = SiteStatus.objects.first()
    return JsonResponse({'maintenance_mode': status.maintenance_mode if status else False})

urlpatterns = [
    path('', aspirex_world, name='aspirex-world'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('unified_auth.urls')),
    path('api/student/', include('student.urls')),
    path('api/mentor/', include('mentor.urls')),
    path('api/chat/', include('chat.urls')),
    path('api/community/', include('community.urls')),
    path('api/events/', include('events.urls')),
    path('api/test-cors/', test_cors, name='test-cors'),
    path('api/platform-stats/', platform_stats, name='platform-stats'),
    path('api/newsletter/', newsletter_subscribe, name='newsletter-subscribe'),
    path('api/site-status/', site_status, name='site-status'),
    path('api/', include(router.urls)),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)