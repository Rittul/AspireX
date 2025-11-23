from django.urls import path,include
from rest_framework.routers import DefaultRouter
from . import views


urlpatterns = [
    path('register/', views.StudentRegistrationAPIView.as_view(), name='register'),
    path('login/', views.StudentLoginAPIView.as_view(), name='login'),
    path('profile/', views.StudentProfileAPIView.as_view(), name='profile'),
    path('profile/update/', views.StudentProfileUpdateAPIView.as_view(), name='student-profile-update'),
    path('profile/file/', views.StudentFileUploadAPIView.as_view(), name='student-cv-update'),
    path('booking/', views.BookingCreateAPIView.as_view(), name='booking-create'),
    path('bookings/', views.BookingListAPIView.as_view(), name='booking-list'),
    path('public/', views.PublicStudentListView.as_view(), name='public-student-list'),
    path('public/<str:student_id>/', views.PublicStudentDetailView.as_view(), name='public-student-detail'),
    path('notes/', views.StudentNoteListCreateView.as_view(), name='student-notes'),
    path('notes/<int:note_id>/', views.StudentNoteDeleteView.as_view(), name='student-note-delete'),
    path('messages/', views.StudentMessageListAPIView.as_view(), name='student-messages'),
    path('messages/<int:pk>/', views.StudentMessageDetailAPIView.as_view(), name='student-message-detail'),
    path('messages/<int:message_id>/read/', views.StudentMessageMarkAsReadAPIView.as_view(), name='student-message-read'),
    path('feedback/', views.FeedbackCreateAPIView.as_view(), name='feedback-create'),
    path('feedback/list/', views.FeedbackListAPIView.as_view(), name='feedback-list'),
    path('feedback/<int:pk>/', views.FeedbackDetailAPIView.as_view(), name='feedback-detail'),
    path('feedback/mentor/<str:mentor_id>/', views.MentorFeedbackListAPIView.as_view(), name='mentor-feedback-list'),
    path('feedback/check/<str:meeting_id>/', views.CheckFeedbackExistsAPIView.as_view(), name='check-feedback-exists'),
] 