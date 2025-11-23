from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from .models import *
from .serializers import *
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework import status
from rest_framework import generics
from .serializers import MentorRegistrationSerializer
from rest_framework.permissions import AllowAny
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.db import models
from django.utils import timezone
from utils import send_credentials_email
from .serializers import PublicMentorSerializer
from rest_framework.authentication import TokenAuthentication as DRFTokenAuthentication
from rest_framework.authentication import get_authorization_header
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import RetrieveAPIView
from django.db.models import Q
from .models import Mentor
from .serializers import MentorSerializer
from mentor.models import Meeting, MeetingAttendance, Mentor
from rest_framework.permissions import IsAuthenticated
from student.models import Student
from student.models import StudentMessage

from django.utils.dateparse import parse_datetime
from django.utils import timezone
import razorpay
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import hmac
import hashlib
from .models import Earning
from student.models import Booking
from django.http import JsonResponse
import json
import os
from decouple import config
from supabase import create_client, Client
import mimetypes
import time
SUPABASE_URL = config('SUPABASE_URL')
SUPABASE_KEY = config('SUPABASE_KEY')
SUPABASE_BUCKET = config('SUPABASE_BUCKET', default='user-uploads')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def extract_supabase_path(url):
    if not url:
        return None
    parts = url.split('/')
    try:
        idx = parts.index(SUPABASE_BUCKET)
        return '/'.join(parts[idx+1:])
    except ValueError:
        return None

class MentorTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Token '):
            return None

        token_key = auth_header.split('Token ')[1]
        try:
            token = MentorToken.objects.get(key=token_key)
            return (token.user, None)
        except MentorToken.DoesNotExist:
            raise AuthenticationFailed('Invalid token')



class MentorMeetingRescheduleAPIView(APIView):
    authentication_classes = [MentorTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, meeting_id):
        mentor = request.user
        new_time_str = request.data.get('new_time')
        if not new_time_str:
            return Response({'error': 'New time is required.'}, status=400)
        new_time = parse_datetime(new_time_str)
        if not new_time:
            return Response({'error': 'Invalid datetime format.'}, status=400)
        new_time = timezone.make_aware(new_time) if timezone.is_naive(new_time) else new_time
        try:
            meeting = Meeting.objects.get(meeting_id=meeting_id, mentor=mentor)
        except Meeting.DoesNotExist:
            return Response({'error': 'Meeting not found.'}, status=404)
        now = timezone.now()
        # Only enforce the 2-hour rule for scheduled meetings
        if meeting.status == 'scheduled' and (meeting.scheduled_time - now).total_seconds() < 2 * 60 * 60:
            return Response({'error': 'Cannot reschedule less than 2 hours before the meeting.'}, status=400)
        if (new_time - now).total_seconds() < 2 * 60 * 60:
            return Response({'error': 'New meeting time must be at least 2 hours from now.'}, status=400)
        meeting.scheduled_time = new_time
        meeting.status = 'scheduled'
        meeting.save(update_fields=['scheduled_time', 'status'])
        # Notify student
        if meeting.student:
            # Convert UTC time to IST for display
            import pytz
            IST = pytz.timezone('Asia/Kolkata')
            new_time_ist = new_time.astimezone(IST)
            StudentMessage.objects.create(
                student=meeting.student,
                sender=None,  # Sender must be a Student instance; None for system/mentor
                subject="Your meeting has been rescheduled",
                                    message=f"Your meeting '{meeting.title}' with {mentor.name} has been rescheduled to {new_time_ist.strftime('%Y-%m-%d %I:%M %p')} IST. If you have any problem, please contact customer support.",
            )
        return Response({'success': True, 'new_time': new_time}, status=200)


class MentorViewSet(viewsets.ModelViewSet):
    queryset = Mentor.objects.all()
    serializer_class = MentorSerializer
    permission_classes = [permissions.IsAuthenticated]


class MentorProfileAPIView(APIView):
    authentication_classes = [MentorTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        mentor = request.user
        # Update online status when mentor accesses profile
        mentor.update_online_status()
        # print("User:", request.user)
        serializer = MentorSerializer(mentor)
        # print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class MentorRegistrationAPIView(generics.CreateAPIView):
    authentication_classes = []
    permission_classes = (permissions.AllowAny,)
    serializer_class = MentorRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mentor = serializer.save()
        token = MentorToken.objects.create(user=mentor)
        # Send welcome email with credentials
        password = request.data.get('password')
        send_credentials_email(
            email=mentor.email,
            username=mentor.mentor_id,
            password=password,
            name=getattr(mentor, 'name', None)
        )
        return Response({
            'mentor': MentorSerializer(mentor).data,
            'token': token.key,
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)

class MentorLoginAPIView(APIView):
    authentication_classes = []
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        serializer = MentorLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mentor = serializer.validated_data['mentor']
        token, created = MentorToken.objects.get_or_create(user=mentor)
        return Response({
            'mentor': MentorSerializer(mentor).data,
            'token': token.key,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)
    




class PublicMentorListView(generics.ListAPIView):
    authentication_classes = []
    queryset = Mentor.objects.all().order_by('mentor_id')
    serializer_class = PublicMentorSerializer
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    lookup_field = 'mentor_id'

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', '')

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(mentor_id__icontains=search)
            )
        return queryset

class PublicMentorDetailView(RetrieveAPIView):
    authentication_classes = []
    queryset = Mentor.objects.all()
    serializer_class = PublicMentorSerializer
    permission_classes = [AllowAny]
    lookup_field = 'mentor_id'
    lookup_url_kwarg = 'mentor_id'



# Add to your views.py
class MentorProfileUpdateAPIView(APIView):
    authentication_classes = [MentorTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request):
        mentor = request.user
        # Update online status when mentor updates profile
        mentor.update_online_status()
        serializer = MentorSerializer(mentor, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        print("PROFILE UPDATE ERRORS:", serializer.errors)  # Debugging line
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MentorCVUpdateAPIView(APIView):
    authentication_classes = [MentorTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request):
        mentor = request.user
        cv_file = request.FILES.get('cv')
        
        if not cv_file:
            return Response(
                {"error": "No file provided"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Validate file type
        valid_extensions = ['.pdf', '.doc', '.docx']
        if not any(cv_file.name.lower().endswith(ext) for ext in valid_extensions):
            return Response(
                {"error": "Invalid file type. Only PDF, DOC, and DOCX are allowed."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if mentor.details.cv:
            mentor.details.cv.delete()
            
        mentor.details.cv = cv_file
        mentor.details.save()
        
        return Response(
            {"cv_url": mentor.details.cv.url},
            status=status.HTTP_200_OK
        )
    
    def delete(self, request):
        mentor = request.user
        if mentor.details.cv:
            mentor.details.cv.delete()
            mentor.details.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"error": "No CV to delete"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    


# Update your MentorCVUpdateAPIView to MentorFileUploadAPIView
class MentorFileUploadAPIView(APIView):
    authentication_classes = [MentorTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request):
        mentor = request.user
        # Update online status when mentor uploads files
        mentor.update_online_status()
        cv_file = request.FILES.get('cv')
        profile_photo = request.FILES.get('profile_photo')
        
        print(f"DEBUG: Files received - cv_file: {cv_file}, profile_photo: {profile_photo}")
        
        if cv_file:
            if getattr(settings, 'USE_SUPABASE', False):
                # Supabase upload logic
                valid_extensions = ['.pdf', '.doc', '.docx']
                ext = os.path.splitext(cv_file.name)[1].lower()
                if ext not in valid_extensions:
                    return Response(
                        {"error": "Invalid file type. Only PDF, DOC, and DOCX are allowed."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                content_type, _ = mimetypes.guess_type(cv_file.name)
                file_options = {"content-type": content_type or "application/octet-stream"}
                file_path = f"mentors/cvs/{cv_file.name}"
                if mentor.details.cv:
                    old_path = extract_supabase_path(mentor.details.cv)
                    if old_path:
                        supabase.storage.from_(SUPABASE_BUCKET).remove([old_path])
                supabase.storage.from_(SUPABASE_BUCKET).remove([file_path])
                res = supabase.storage.from_(SUPABASE_BUCKET).upload(file_path, cv_file.read(), file_options=file_options)
                public_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(file_path)
                if public_url:
                    public_url = public_url.strip()
                    while public_url.endswith('?') or public_url.endswith(' '):
                        public_url = public_url.rstrip('? ').rstrip()
                    if not public_url.startswith(('http://', 'https://')):
                        public_url = 'https://' + public_url.lstrip('/')
                print(f"DEBUG: Final CV URL to save: '{public_url}' (type: {type(public_url)})")
                print(f"DEBUG: repr(public_url): {repr(public_url)}")
                from django.core.validators import URLValidator
                from django.core.exceptions import ValidationError
                try:
                    URLValidator()(public_url)
                    print("DEBUG: URL validation passed")
                except ValidationError as e:
                    print(f"DEBUG: URL validation failed: {e}")
                    return Response(
                        {"error": f"Invalid URL generated: {public_url}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                mentor.details.cv = public_url
            else:
                # Local storage
                file_path = default_storage.save(f"cvs/{cv_file.name}", cv_file)
                public_url = settings.MEDIA_URL + file_path
                mentor.details.cv = public_url
            mentor.details.save()
            return Response(
                {"cv_url": mentor.details.cv},
                status=status.HTTP_200_OK
            )
        elif profile_photo:
            print(f"DEBUG: Processing profile photo: {profile_photo.name}")
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            ext = os.path.splitext(profile_photo.name)[1].lower()
            if ext not in valid_extensions:
                return Response(
                    {"error": "Invalid file type. Only JPG, JPEG, PNG, and GIF are allowed."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                # Use a unique filename: mentorID_timestamp.ext
                unique_filename = f"{mentor.mentor_id}_{int(time.time())}{ext}"
                file_content = profile_photo.read()
                print(f"DEBUG: File size: {len(file_content)} bytes")
                
                content_type, _ = mimetypes.guess_type(profile_photo.name)
                file_options = {"content-type": content_type or "image/jpeg"}
                file_path = f"mentors/profile_photos/{unique_filename}"
                
                print(f"DEBUG: Uploading to path: {file_path}")
                
                # Delete old file if exists (from the URL in the model)
                if mentor.details.profile_photo:
                    old_path = extract_supabase_path(mentor.details.profile_photo)
                    if old_path:
                        print(f"DEBUG: Removing old file: {old_path}")
                        supabase.storage.from_(SUPABASE_BUCKET).remove([old_path])
                
                # Upload new file
                res = supabase.storage.from_(SUPABASE_BUCKET).upload(file_path, file_content, file_options=file_options)
                print(f"DEBUG: Upload result: {res}")
                
                public_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(file_path)
                if public_url:
                    public_url = public_url.strip()
                    # Remove trailing '?' and any whitespace
                    while public_url.endswith('?') or public_url.endswith(' '):
                        public_url = public_url.rstrip('? ').rstrip()
                    # Ensure it starts with http/https
                    if not public_url.startswith(('http://', 'https://')):
                        public_url = 'https://' + public_url.lstrip('/')
                print(f"DEBUG: Final profile photo URL to save: '{public_url}'")
                
                # Validate URL before saving
                from django.core.validators import URLValidator
                from django.core.exceptions import ValidationError
                try:
                    URLValidator()(public_url)
                    print(f"DEBUG: Profile photo URL validation passed")
                except ValidationError as e:
                    print(f"DEBUG: Profile photo URL validation failed: {e}")
                    return Response(
                        {"error": f"Invalid URL generated: {public_url}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                mentor.details.profile_photo = public_url
                mentor.details.save()
                print(f"DEBUG: Profile photo URL saved to database: {mentor.details.profile_photo}")
                return Response(
                    {"profile_photo_url": public_url},
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                print(f"DEBUG: Error uploading profile photo: {str(e)}")
                return Response(
                    {"error": f"Failed to upload profile photo: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(
            {"error": "No file provided"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def delete(self, request):
        mentor = request.user
        file_type = request.query_params.get('type') or request.data.get('type')
        if not file_type:
            file_type = 'cv'  # Default to 'cv' if not provided

        if file_type == 'cv' and mentor.details.cv:
            # Remove from Supabase if possible
            old_path = extract_supabase_path(mentor.details.cv)
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Attempting to delete CV from Supabase: {old_path}")
            if old_path:
                try:
                    res = supabase.storage.from_(SUPABASE_BUCKET).remove([old_path])
                    logger.info(f"Supabase remove result: {res}")
                except Exception as e:
                    logger.error(f"Error deleting CV from Supabase: {e}")
            mentor.details.cv = None
            mentor.details.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif file_type == 'profile_photo' and mentor.details.profile_photo:
            mentor.details.profile_photo = None
            mentor.details.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"error": f"No {file_type} to delete"},
            status=status.HTTP_400_BAD_REQUEST
        )
    


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def filtered_mentor_list(request):
    search = request.GET.get('search')
    category = request.GET.get('category')

    mentors = Mentor.objects.select_related('details').all()

    if search:
        mentors = mentors.filter(
        Q(name__icontains=search) |
        Q(details__professions__title__icontains=search)
    )

    if category:
        mentors = mentors.filter(details__professions__title__icontains=category)

    mentors = mentors.distinct()
    serializer = MentorSerializer(mentors, many=True)
    return Response(serializer.data)





class MentorNoteListCreateView(generics.ListCreateAPIView):
    authentication_classes = [MentorTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MentorNoteSerializer

    def get_queryset(self):
        user = self.request.user
        try:
            return MentorNote.objects.filter(mentor=user)
        except Mentor.DoesNotExist:
            return MentorNote.objects.none()

    def perform_create(self, serializer):
        serializer.save(mentor=self.request.user)

class MentorNoteDeleteView(generics.DestroyAPIView):
    serializer_class = MentorNoteSerializer
    authentication_classes = [MentorTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'note_id'

    def get_queryset(self):
        return MentorNote.objects.filter(mentor=self.request.user)

# Earnings API Views
class MentorEarningsAPIView(APIView):
    authentication_classes = [MentorTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        mentor = request.user
        time_filter = request.query_params.get('time_filter', 'all')
        
        # Get earnings based on time filter
        earnings = Earning.objects.filter(mentor=mentor, status='completed')
        
        if time_filter == '7days':
            from datetime import timedelta
            earnings = earnings.filter(date__gte=timezone.now().date() - timedelta(days=7))
        elif time_filter == '30days':
            from datetime import timedelta
            earnings = earnings.filter(date__gte=timezone.now().date() - timedelta(days=30))
        elif time_filter == '3months':
            from datetime import timedelta
            earnings = earnings.filter(date__gte=timezone.now().date() - timedelta(days=90))
        
        # Calculate statistics - only positive earnings (exclude withdrawals)
        positive_earnings = earnings.filter(amount__gt=0)
        total_earnings = positive_earnings.aggregate(total=models.Sum('amount'))['total'] or 0
        total_sessions = positive_earnings.count()
        
        # Get unique students by extracting student names from source
        # Source format: "Session Type with Student Name"
        student_sources = positive_earnings.values_list('source', flat=True)
        unique_students = set()
        for source in student_sources:
            if 'with' in source.lower():
                # Extract student name after "with"
                student_name = source.split('with')[-1].strip()
                unique_students.add(student_name)
        total_students = len(unique_students)
        
        # Available balance (total positive earnings minus withdrawals)
        total_withdrawals = Withdrawal.objects.filter(
            mentor=mentor,
            status__in=['pending', 'approved', 'processed']
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        available_balance = total_earnings - total_withdrawals
        
        # Paginate earnings
        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginated_earnings = paginator.paginate_queryset(earnings, request)
        
        earnings_serializer = EarningSerializer(paginated_earnings, many=True)
        
        return Response({
            'earnings': earnings_serializer.data,
            'stats': {
                'totalEarnings': float(total_earnings),
                'totalSessions': total_sessions,
                'totalStudents': total_students,
                'availableBalance': float(available_balance)
            },
            'pagination': {
                'count': paginator.page.paginator.count,
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
                'current_page': paginator.page.number,
                'total_pages': paginator.page.paginator.num_pages
            }
        }, status=status.HTTP_200_OK)

class MentorWithdrawalAPIView(APIView):
    authentication_classes = [MentorTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get all withdrawals for the mentor"""
        mentor = request.user
        withdrawals = Withdrawal.objects.filter(mentor=mentor).order_by('-request_date')
        serializer = WithdrawalSerializer(withdrawals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        """Create a new withdrawal request"""
        mentor = request.user
        amount = request.data.get('amount')
        bank_details = request.data.get('bank_details', '')
        payment_method = request.data.get('payment_method', 'bank_transfer')
        
        if not amount:
            return Response(
                {"error": "Amount is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            amount = float(amount)
        except ValueError:
            return Response(
                {"error": "Invalid amount"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check minimum withdrawal amount
        if amount < 50.00:
            return Response(
                {"error": "Minimum withdrawal amount is $50.00"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if mentor has sufficient balance
        # Get total positive earnings
        positive_earnings = Earning.objects.filter(
            mentor=mentor, 
            status='completed',
            amount__gt=0
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        # Get total withdrawals (pending, approved, processed)
        total_withdrawals = Withdrawal.objects.filter(
            mentor=mentor,
            status__in=['pending', 'approved', 'processed']
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        available_balance = float(positive_earnings) - float(total_withdrawals)
        
        if amount > available_balance:
            return Response(
                {"error": f"Insufficient balance. Available: ${available_balance:.2f}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create withdrawal record
        withdrawal_data = {
            'mentor': mentor,
            'amount': amount,
            'payment_method': payment_method,
            'bank_details': bank_details,
            'status': 'pending'
        }
        
        withdrawal = Withdrawal.objects.create(**withdrawal_data)
        serializer = WithdrawalSerializer(withdrawal)
        
        return Response({
            "message": f"Withdrawal request for ${amount} submitted successfully",
            "withdrawal": serializer.data
        }, status=status.HTTP_201_CREATED)

class MentorEarningsExportAPIView(APIView):
    authentication_classes = [MentorTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        mentor = request.user
        time_filter = request.query_params.get('time_filter', 'all')
        
        earnings = Earning.objects.filter(mentor=mentor, status='completed').order_by('-date')
        
        if time_filter == '7days':
            from datetime import timedelta
            earnings = earnings.filter(date__gte=timezone.now().date() - timedelta(days=7))
        elif time_filter == '30days':
            from datetime import timedelta
            earnings = earnings.filter(date__gte=timezone.now().date() - timedelta(days=30))
        elif time_filter == '3months':
            from datetime import timedelta
            earnings = earnings.filter(date__gte=timezone.now().date() - timedelta(days=90))
        
        earnings_serializer = EarningSerializer(earnings, many=True)
        
        return Response({
            'earnings': earnings_serializer.data,
            'export_date': timezone.now().isoformat(),
            'mentor_name': mentor.name,
            'mentor_id': mentor.mentor_id
        }, status=status.HTTP_200_OK)

class MentorFeedbackListAPIView(generics.ListAPIView):
    """
    List all feedback received by the authenticated mentor
    """
    authentication_classes = [MentorTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MentorFeedbackSerializer
    
    def get_queryset(self):
        from student.models import Feedback
        return Feedback.objects.filter(mentor=self.request.user).order_by('-created_at')

class MentorFeedbackDetailAPIView(generics.RetrieveAPIView):
    """
    Retrieve a specific feedback detail
    """
    authentication_classes = [MentorTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MentorFeedbackSerializer
    
    def get_queryset(self):
        from student.models import Feedback
        return Feedback.objects.filter(mentor=self.request.user)

class MentorFeedbackStatsAPIView(APIView):
    """
    Get feedback statistics for the mentor
    """
    authentication_classes = [MentorTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        from student.models import Feedback
        from django.db.models import Avg, Count
        
        mentor = request.user
        feedbacks = Feedback.objects.filter(mentor=mentor)
        
        stats = {
            'total_feedback': feedbacks.count(),
            'average_rating': feedbacks.aggregate(Avg('rating'))['rating__avg'] or 0,
            'rating_distribution': feedbacks.values('rating').annotate(count=Count('rating')).order_by('rating'),
            'approved_feedback': feedbacks.filter(is_approved=True).count(),
            'pending_feedback': feedbacks.filter(is_approved=False).count(),
        }
        
        return Response(stats, status=status.HTTP_200_OK)





# Custom permission to allow both mentor and student tokens
class IsMentorOrStudentAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

class DualTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != b'token':
            return None
        token_key = auth[1].decode() if len(auth) > 1 else None
        if not token_key:
            return None
            
        # Try MentorTokenAuthentication first
        from mentor.models import MentorToken
        try:
            mentor_token = MentorToken.objects.get(key=token_key)
            return (mentor_token.user, None)
        except MentorToken.DoesNotExist:
            pass
            
        # Try DRF TokenAuthentication (for students)
        try:
            from rest_framework.authtoken.models import Token
            student_token = Token.objects.get(key=token_key)
            return (student_token.user, None)
        except Token.DoesNotExist:
            pass
            
        return None

@api_view(['GET', 'POST'])
@authentication_classes([DualTokenAuthentication])
@permission_classes([IsMentorOrStudentAuthenticated])
def record_meeting_attendance(request):
    if request.method == 'POST':
        meeting_id = request.data.get('meeting_id')
        role = request.data.get('role')  # 'mentor' or 'student'
        entered_key = request.data.get('attendance_key')
        
        if not meeting_id or role not in ['mentor', 'student'] or not entered_key:
            return Response({'error': 'meeting_id, role, and attendance_key are required.'}, status=400)
        try:
            meeting = Meeting.objects.get(meeting_id=meeting_id)
        except Meeting.DoesNotExist:
            return Response({'error': 'Meeting not found.'}, status=404)
        user = request.user
        # Use isinstance for robust role validation
        if role == 'mentor' and not isinstance(user, Mentor):
            return Response({'error': 'Only mentors can record mentor attendance.'}, status=403)
        if role == 'student' and not isinstance(user, Student):
            return Response({'error': 'Only students can record student attendance.'}, status=403)
        
        # Validate that the user is associated with this meeting
        if role == 'mentor' and meeting.mentor != user:
            return Response({'error': 'You can only mark attendance for your own meetings.'}, status=403)
        if role == 'student' and meeting.student != user:
            return Response({'error': 'You can only mark attendance for your own meetings.'}, status=403)
        
        # Cross-verification: mentor must enter student's key, student must enter mentor's key
        if role == 'mentor':
            if entered_key != meeting.student_attendance_key:
                return Response({'error': 'Invalid attendance key for mentor.'}, status=403)
            if meeting.mentor_attended:
                return Response({'message': 'Mentor attendance already marked.'}, status=200)
            meeting.mentor_attended = True
            meeting.mentor_attendance_time = timezone.now()
            meeting.save(update_fields=['mentor_attended', 'mentor_attendance_time'])
            # Create MeetingAttendance record
            MeetingAttendance.objects.get_or_create(
                meeting=meeting,
                user_id=user.mentor_id,
                role='mentor'
            )
            # If both attended, mark as completed
            if meeting.student_attended and meeting.mentor_attended:
                meeting.status = 'completed'
                meeting.save(update_fields=['status'])
            return Response({'success': True, 'message': 'Mentor attendance marked.'})
        elif role == 'student':
            if entered_key != meeting.mentor_attendance_key:
                return Response({'error': 'Invalid attendance key for student.'}, status=403)
            if meeting.student_attended:
                return Response({'message': 'Student attendance already marked.'}, status=200)
            meeting.student_attended = True
            meeting.student_attendance_time = timezone.now()
            meeting.save(update_fields=['student_attended', 'student_attendance_time'])
            # Create MeetingAttendance record
            MeetingAttendance.objects.get_or_create(
                meeting=meeting,
                user_id=user.student_id,
                role='student'
            )
            # If both attended, mark as completed
            if meeting.student_attended and meeting.mentor_attended:
                meeting.status = 'completed'
                meeting.save(update_fields=['status'])
            return Response({'success': True, 'message': 'Student attendance marked.'})
    elif request.method == 'GET':
        meeting_id = request.GET.get('meeting_id')
        if not meeting_id:
            return Response({'error': 'meeting_id is required.'}, status=400)
        try:
            meeting = Meeting.objects.get(meeting_id=meeting_id)
        except Meeting.DoesNotExist:
            return Response({'error': 'Meeting not found.'}, status=404)
        attended_roles = []
        if meeting.mentor_attended:
            attended_roles.append('mentor')
        if meeting.student_attended:
            attended_roles.append('student')
        return Response({
            'student_attended': meeting.student_attended,
            'mentor_attended': meeting.mentor_attended,
            'student_attendance_time': meeting.student_attendance_time,
            'mentor_attendance_time': meeting.mentor_attendance_time,
            'attended_roles': attended_roles
        })





class CreateOrderAPIView(APIView):
    authentication_classes = [MentorTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')
        booking_id = request.data.get('booking_id')
        if not amount or float(amount) <= 0:
            return Response({'error': 'Invalid amount'}, status=400)
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        order = client.order.create({
            'amount': int(float(amount) * 100),  # paise
            'currency': 'INR',
            'payment_capture': 1
        })
        # Link order_id to Booking if booking_id is provided
        if booking_id:
            try:
                booking = Booking.objects.get(id=booking_id, student=request.user)
                booking.transaction_id = order['id']
                booking.save()
            except Booking.DoesNotExist:
                return Response({'error': 'Invalid booking_id'}, status=400)
        return Response({'order': order, 'key_id': settings.RAZORPAY_KEY_ID})

class VerifyPaymentAPIView(APIView):
    authentication_classes = [MentorTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        order_id = data.get('order_id')
        payment_id = data.get('razorpay_payment_id')
        signature = data.get('razorpay_signature')
        booking_id = data.get('booking_id')
        if not (order_id and payment_id and signature and booking_id):
            return Response({'error': 'Missing data'}, status=400)
        msg = f"{order_id}|{payment_id}"
        generated_signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(),
            msg.encode(),
            hashlib.sha256
        ).hexdigest()
        if generated_signature == signature:
            # Mark Booking as paid, update transaction_id, and create Earning
            try:
                booking = Booking.objects.get(id=booking_id, student=request.user, transaction_id=order_id)
                booking.is_paid = True
                booking.transaction_id = order_id
                booking.save()
                
                # Create Earning for mentor if not already exists
                from mentor.models import Earning
                if not Earning.objects.filter(transaction_id=order_id).exists():
                    # Use service price from booking if available, otherwise fall back to mentor fees
                    if booking.service_price:
                        amount = booking.service_price
                    else:
                        amount = booking.mentor.details.fees if hasattr(booking.mentor, 'details') else 0
                        
                    Earning.objects.create(
                        mentor=booking.mentor,
                        amount=amount,
                        source=f"Session with {booking.student.name} (Booking {booking.id}) - {booking.service if booking.service else 'Service'}",
                        transaction_id=order_id,
                        status='completed'
                    )
                
                # Send payment confirmation notifications
                from mentor.models import MentorMessage
                from student.models import StudentMessage
                from django.utils import timezone
                import pytz
                
                IST = pytz.timezone('Asia/Kolkata')
                current_time = timezone.now().astimezone(IST)
                
                # Send mentor notification about payment received
                MentorMessage.objects.create(
                    mentor=booking.mentor,
                    subject="💰 Payment Received for Booking",
                    message=(
                        f"Payment received for your booking with {booking.student.name}.\n\n"
                        f"Subject: {booking.subject}\n"
                        f"Service: {booking.service}\n"
                        f"Amount: ₹{booking.service_price}\n"
                        f"Duration: {booking.service_duration}\n"
                        f"Payment Time: {current_time.strftime('%Y-%m-%d %I:%M %p')} IST\n"
                        f"Transaction ID: {order_id}\n\n"
                        f"Your meeting will be scheduled automatically. You will receive meeting details shortly."
                    ),
                    admin_sender=None
                )
                
                # Send student notification about payment confirmation
                StudentMessage.objects.create(
                    student=booking.student,
                    subject="Payment Confirmed",
                    message=(
                        f"Your payment has been confirmed for the booking with {booking.mentor.name}.\n\n"
                        f"Subject: {booking.subject}\n"
                        f"Service: {booking.service}\n"
                        f"Amount Paid: ₹{booking.service_price}\n"
                        f"Duration: {booking.service_duration}\n"
                        f"Payment Time: {current_time.strftime('%Y-%m-%d %I:%M %p')} IST\n"
                        f"Transaction ID: {order_id}\n\n"
                        f"Your meeting will be scheduled automatically. You will receive meeting details shortly."
                    ),
                    sender=None
                )
            except Booking.DoesNotExist:
                return Response({'error': 'Invalid booking or order'}, status=400)
            return Response({'status': 'Payment verified'})
        else:
            return Response({'status': 'Payment verification failed'}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class RazorpayWebhookAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        # Validate Razorpay webhook signature
        webhook_secret = settings.RAZORPAY_KEY_SECRET  # Or use a separate webhook secret
        received_sig = request.headers.get('X-Razorpay-Signature')
        body = request.body
        generated_sig = hmac.new(webhook_secret.encode(), body, hashlib.sha256).hexdigest()
        if received_sig != generated_sig:
            return JsonResponse({'error': 'Invalid signature'}, status=400)
        data = json.loads(body)
        event = data.get('event')
        # Handle events: payment.captured, payment.failed, refund.processed, etc.
        # Update Earning/Booking as needed
        return JsonResponse({'status': 'ok'})





# Add this new view for updating online status
@api_view(['POST'])
@authentication_classes([MentorTokenAuthentication])
@permission_classes([IsAuthenticated])
def update_online_status(request):
    """Update mentor's online status"""
    try:
        mentor = request.user
        print(f"Updating online status for mentor: {mentor.name} ({mentor.mentor_id})")
        
        # Check if we should set offline status
        set_offline = request.data.get('set_offline', False)
        
        if set_offline:
            # Set last activity to 10 minutes ago to make mentor offline
            from datetime import timedelta
            mentor.last_activity = timezone.now() - timedelta(minutes=10)
            mentor.is_online = False
            mentor.save(update_fields=['last_activity', 'is_online'])
            print(f"Set {mentor.name} as offline")
        else:
            # Normal online status update
            mentor.update_online_status()
            print(f"Updated {mentor.name} online status")
        
        return Response({
            'is_online': mentor.is_currently_online(),
            'last_activity': mentor.last_activity.isoformat() if mentor.last_activity else None
        }, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error in update_online_status: {e}")
        return Response({
            'error': 'Failed to update online status'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




