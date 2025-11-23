from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
import secrets
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model


class MentorManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        # Use transaction.atomic as a context manager
        with transaction.atomic():
            user = self.model(
                email=email,
                name=name,
                **extra_fields
            )
            user.set_password(password)
            user.save(using=self._db)

            if not user.mentor_id:
                last_id = Mentor.objects.aggregate(
                    max_id=models.Max('id')
                )['max_id'] or 0
                user.mentor_id = f"M{str(last_id).zfill(6)}"
                user.save(update_fields=['mentor_id'])
            return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, name, password, **extra_fields)

class Mentor(AbstractUser):
    email = models.EmailField(unique=True)
    mentor_id = models.CharField(max_length=10, unique=True, blank=True)
    name = models.CharField(max_length=100)
    accepted_terms = models.BooleanField(default=False)
    
    # Online status fields
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(auto_now=True)

    username = None

    groups = models.ManyToManyField(
        Group,
        related_name='mentor_user_set',
        blank=True,
        help_text='Groups this mentor belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='mentor_user_permissions',
        blank=True,
        help_text='User-specific permissions for this mentor.',
        verbose_name='user permissions',
    )

    USERNAME_FIELD = 'mentor_id'
    REQUIRED_FIELDS = ['email', 'name']
    
    objects = MentorManager()
    
    def __str__(self):
        return f"{self.mentor_id} - {self.name}"

    def is_currently_online(self):
        """Check if mentor is currently online based on last activity"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Consider online if last activity was within 5 minutes
        five_minutes_ago = timezone.now() - timedelta(minutes=5)
        
        # Update the is_online field based on current activity
        is_online = self.last_activity >= five_minutes_ago
        if self.is_online != is_online:
            self.is_online = is_online
            self.save(update_fields=['is_online'])
        
        return is_online

    def update_online_status(self):
        """Update the online status based on current activity"""
        from django.utils import timezone
        
        self.last_activity = timezone.now()
        self.last_seen = timezone.now()
        self.is_online = True
        self.save(update_fields=['last_activity', 'last_seen', 'is_online'])

    def save(self, *args, **kwargs):
        if not self.mentor_id and not kwargs.get('update_fields') == ['mentor_id']:
            # Use transaction.atomic as a context manager
            with transaction.atomic():
                max_id = Mentor.objects.aggregate(
                    max_id=models.Max('id')
                )['max_id'] or 0
                self.mentor_id = f"M{str(max_id + 1).zfill(6)}"
        super().save(*args, **kwargs)



class MentorToken(models.Model):
    key = models.CharField(_("Key"), max_length=40, primary_key=True)
    user = models.OneToOneField(
        'Mentor',
        related_name='auth_token',
        on_delete=models.CASCADE,
        verbose_name=_("Mentor")
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True)

    class Meta:
        verbose_name = _("Mentor Token")
        verbose_name_plural = _("Mentor Tokens")

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    @classmethod
    def generate_key(cls):
        return secrets.token_hex(20)  # Generates a 40-character hex token

    def __str__(self):
        return self.key
    




@admin.register(Mentor)
class MentorAdmin(UserAdmin):
    list_display = ('mentor_id', 'email', 'name', 'is_staff')
    search_fields = ('mentor_id', 'email', 'name')
    ordering = ('mentor_id',)
    
    fieldsets = (
        (None, {'fields': ('mentor_id', 'email', 'password')}),
        ('Personal info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )



class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True) 

    def __str__(self):
        return self.name

class Profession(models.Model):
    title = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.title


class MentorDetail(models.Model):
    mentor = models.OneToOneField(
        Mentor, 
        on_delete=models.CASCADE,
        related_name='details',
        primary_key=True  # This makes the mentor_id the primary key of MentorDetail
    )
    
    # Add Details     
    first_name = models.CharField(max_length=200, default="", blank=True)
    last_name = models.CharField(max_length=200, default="", blank=True)
    dob = models.DateField(null=True, blank=True)
    age = models.PositiveIntegerField(default=0)
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male')
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=False, default="", blank=True)

    college = models.CharField(max_length=400, default="", blank=True)
    cgpa = models.FloatField(default=0.0)
    batch = models.PositiveIntegerField(default=2000)
    
    professions = models.ManyToManyField(Profession, related_name='mentors', blank=True)
    skills = models.ManyToManyField(Skill, related_name='mentors', blank=True)

    fees = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    about = models.TextField(default="", blank=True)
    availability_timings = models.CharField(max_length=50, default="", blank=True)
    profile_photo = models.URLField(max_length=500, null=True, blank=True, default=None)
    cv = models.TextField(max_length=1000, null=True, blank=True, default=None)

    is_approved = models.BooleanField(default=False)

    total_students = models.PositiveIntegerField(default=0)
    total_sessions = models.PositiveIntegerField(default=0)
    average_rating = models.FloatField(default=0.0)
    years_of_experience = models.PositiveIntegerField(default=0)

    linkedin_url = models.CharField(max_length=250,blank=True, null=True)
    github_url = models.CharField(max_length=250,blank=True, null=True)
    portfolio_url = models.CharField(max_length=250,blank=True, null=True)

    # New fields for key achievements, services, availability, languages
    key_achievements = models.JSONField(default=list, blank=True, help_text="List of key achievements")
    services = models.JSONField(default=list, blank=True, help_text="List of services offered")
    availability_day_wise = models.JSONField(default=dict, blank=True, help_text="Availability schedule by day")
    languages = models.JSONField(default=list, blank=True, help_text="List of languages spoken")

    def __str__(self):
        return f"{self.mentor.mentor_id} - {self.first_name} {self.last_name}"
    


class Earning(models.Model):
    mentor = models.ForeignKey(
        Mentor,
        on_delete=models.CASCADE,
        related_name='earnings'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Earning amount in INR (₹)"
    )
    date = models.DateField(
        default=timezone.now,
        help_text="Date when the earning was received"
    )
    source = models.CharField(
        max_length=100,
        help_text="Source of the earning (e.g., Session with Student X)"
    )
    transaction_id = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        help_text="Payment gateway transaction ID if available"
    )
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default='completed'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Any additional notes about this earning"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        verbose_name = "Mentor Earning"
        verbose_name_plural = "Mentor Earnings"

    def __str__(self):
        return f"{self.mentor.mentor_id} - ₹{self.amount} - {self.date}"

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            # Generate a simple transaction ID if none provided
            self.transaction_id = f"TRX-{timezone.now().strftime('%Y%m%d')}-{self.mentor.mentor_id}-{Earning.objects.filter(mentor=self.mentor).count() + 1}"
        super().save(*args, **kwargs)



class MentorMessage(models.Model):
    # Auto-generated UUID field (in addition to default id)
    message_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    mentor = models.ForeignKey(
        Mentor,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    subject = models.CharField(max_length=400)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    admin_sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mentor_sent_messages'
    )

    class Meta:
        ordering = ['-sent_at']
        verbose_name = "Mentor Message"
        verbose_name_plural = "Mentor Messages"

    def __str__(self):
        return f"Message to {self.mentor.name}: {self.subject} (ID: {self.message_id})"

    def mark_as_read(self):
        self.is_read = True
        self.save(update_fields=['is_read'])


class MeetingAttendance(models.Model):
    meeting = models.ForeignKey('Meeting', on_delete=models.CASCADE, related_name='attendances')
    user_id = models.CharField(max_length=100)  # Can be mentor_id or student_id
    role = models.CharField(max_length=10, choices=[('mentor', 'Mentor'), ('student', 'Student')])
    attended_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('meeting', 'user_id', 'role')
        ordering = ['attended_at']

    def __str__(self):
        return f"{self.role} {self.user_id} attended {self.meeting.meeting_id} at {self.attended_at}"


class Meeting(models.Model):
    MEETING_STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('missed', 'Missed'),
    ]

    meeting_id = models.CharField(max_length=16, unique=True, editable=False)
    mentor = models.ForeignKey(
        Mentor,
        on_delete=models.CASCADE,
        related_name='meetings'
    )
    student = models.ForeignKey(
        'student.Student',  # Adjust this to your student model path
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mentor_meetings'
    )
    title = models.CharField(max_length=400)
    description = models.TextField(blank=True)
    scheduled_time = models.DateTimeField()
    duration = models.PositiveIntegerField(help_text="Duration in minutes", default=60)
    meeting_link = models.URLField(blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=MEETING_STATUS_CHOICES,
        default='scheduled'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Attendance system fields
    student_attendance_key = models.CharField(max_length=16, unique=True, null=True, blank=True)
    mentor_attendance_key = models.CharField(max_length=16, unique=True, null=True, blank=True)
    student_attended = models.BooleanField(default=False)
    mentor_attended = models.BooleanField(default=False)
    student_attendance_time = models.DateTimeField(null=True, blank=True)
    mentor_attendance_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-scheduled_time']
        verbose_name = "Mentor Meeting"
        verbose_name_plural = "Mentor Meetings"
        indexes = [
            models.Index(fields=['meeting_id']),
            models.Index(fields=['mentor']),
            models.Index(fields=['status']),
            models.Index(fields=['scheduled_time']),
        ]

    def __str__(self):
        return f"{self.meeting_id} - {self.title} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        # Ensure scheduled_time is timezone-aware
        from django.utils import timezone
        if self.scheduled_time and timezone.is_naive(self.scheduled_time):
            self.scheduled_time = timezone.make_aware(self.scheduled_time)
        # Generate unique student_attendance_key if missing
        if not self.student_attendance_key:
            while True:
                key = secrets.token_urlsafe(8)
                if not Meeting.objects.filter(student_attendance_key=key).exists():
                    self.student_attendance_key = key
                    break
        # Generate unique mentor_attendance_key if missing
        if not self.mentor_attendance_key:
            while True:
                key = secrets.token_urlsafe(8)
                if not Meeting.objects.filter(mentor_attendance_key=key).exists():
                    self.mentor_attendance_key = key
                    break
        # Set meeting_id if not set
        if not self.meeting_id:
            # Save first to get pk
            super().save(*args, **kwargs)
            self.meeting_id = self.generate_meeting_id()
            # Now generate the meeting link using the new meeting_id
            room_name = f"aspirex-{self.meeting_id}-{uuid.uuid4().hex[:8]}"
            self.meeting_link = f"https://meet.jit.si/{room_name}"
            super().save(update_fields=['meeting_id', 'meeting_link'])
            return
        # Ensure meeting_link is set if missing
        if not self.meeting_link:
            room_name = f"aspirex-{self.meeting_id}-{uuid.uuid4().hex[:8]}"
            self.meeting_link = f"https://meet.jit.si/{room_name}"
        self.update_status_based_on_time()
        super().save(*args, **kwargs)

    def generate_meeting_id(self):
        timestamp = timezone.now().strftime("%d%m%y")
        random_str = secrets.token_hex(2).upper()
        return f"MTG-{timestamp}-{random_str}-{self.pk}"

    def update_status_based_on_time(self):
        now = timezone.now()
        end_time = self.scheduled_time + timezone.timedelta(minutes=self.duration)

        if self.status == 'scheduled':
            if now > end_time:
                self.status = 'missed'  # Mark as missed if scheduled time has passed and meeting not attended
            elif self.scheduled_time <= now <= end_time:
                self.status = 'ongoing'

        elif self.status == 'ongoing' and now > end_time:
            self.status = 'completed'

    @property
    def is_upcoming(self):
        return self.status == 'scheduled' and self.scheduled_time > timezone.now()

    @property
    def is_ongoing(self):
        now = timezone.now()
        return (self.status == 'ongoing' or 
                (self.status == 'scheduled' and 
                 now >= self.scheduled_time and 
                 now <= self.scheduled_time + timezone.timedelta(minutes=self.duration)))

    @property
    def is_completed(self):
        return self.status == 'completed'

    @property
    def end_time(self):
        return self.scheduled_time + timezone.timedelta(minutes=self.duration)

    def has_attended(self, role):
        return self.attendances.filter(role=role).exists()
    



class MentorPost(models.Model):
    POST_TYPES = [
        ('TEXT', 'Text'),
        ('IMAGE', 'Image'),
        ('VIDEO', 'Video'),
        ('QUOTE', 'Quote'),
    ]
    
    mentor = models.ForeignKey(
        Mentor,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    post_type = models.CharField(max_length=5, choices=POST_TYPES)
    content = models.TextField()
    image = models.ImageField(upload_to='mentor_posts/images/', null=True, blank=True)
    video = models.FileField(upload_to='mentor_posts/videos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True)

    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.mentor.name}'s {self.get_post_type_display()} post"
    

class MentorNote(models.Model):
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name="notes")
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.mentor.mentor_id} - {self.title}"


class Withdrawal(models.Model):
    WITHDRAWAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('processed', 'Processed'),
        ('cancelled', 'Cancelled'),
    ]

    mentor = models.ForeignKey(
        Mentor,
        on_delete=models.CASCADE,
        related_name='withdrawals'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Withdrawal amount in USD"
    )
    request_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Date when the withdrawal was requested"
    )
    processed_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date when the withdrawal was processed"
    )
    status = models.CharField(
        max_length=10,
        choices=WITHDRAWAL_STATUS_CHOICES,
        default='pending'
    )
    payment_method = models.CharField(
        max_length=50,
        default='bank_transfer',
        help_text="Payment method for withdrawal"
    )
    bank_details = models.TextField(
        blank=True,
        null=True,
        help_text="Bank account details for transfer"
    )
    admin_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Admin notes about this withdrawal"
    )
    transaction_id = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        help_text="Payment gateway transaction ID if available"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-request_date']
        verbose_name = "Mentor Withdrawal"
        verbose_name_plural = "Mentor Withdrawals"

    def __str__(self):
        return f"{self.mentor.mentor_id} - ${self.amount} - {self.status}"

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            # Generate a simple transaction ID if none provided
            self.transaction_id = f"WD-{timezone.now().strftime('%Y%m%d')}-{self.mentor.mentor_id}-{Withdrawal.objects.filter(mentor=self.mentor).count() + 1}"
        super().save(*args, **kwargs)