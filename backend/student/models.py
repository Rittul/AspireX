from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.apps import apps



class StudentManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        with transaction.atomic():
            user = self.model(
                email=email,
                name=name,
                **extra_fields
            )
            user.set_password(password)
            user.save(using=self._db)

            if not user.student_id:
                last_id = Student.objects.aggregate(
                    max_id=models.Max('id')
                )['max_id'] or 0
                user.student_id = f"S{str(last_id).zfill(6)}"
                user.save(update_fields=['student_id'])
            
            return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, name, password, **extra_fields)

class Student(AbstractUser):
    email = models.EmailField(unique=True)
    student_id = models.CharField(max_length=10, unique=True, blank=True)
    name = models.CharField(max_length=100)
    accepted_terms = models.BooleanField(default=False)

    username = None

    groups = models.ManyToManyField(
        Group,
        related_name='student_user_set',
        blank=True,
        help_text='Groups this student belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='student_user_permissions',
        blank=True,
        help_text='User-specific permissions for this student.',
        verbose_name='user permissions',
    )

    USERNAME_FIELD = 'student_id'
    REQUIRED_FIELDS = ['email', 'name']
    
    objects = StudentManager()
    
    def __str__(self):
        return f"{self.student_id} - {self.name}"

    def save(self, *args, **kwargs):
        # Use transaction.atomic as a context manager if needed
        if not self.student_id and not kwargs.get('update_fields') == ['student_id']:
            with transaction.atomic():
                max_id = Student.objects.aggregate(
                    max_id=models.Max('id')
                )['max_id'] or 0
                self.student_id = f"S{str(max_id).zfill(6)}"
                super().save(*args, **kwargs)
                return
        super().save(*args, **kwargs)

@receiver(post_save, sender=Student)
def create_student_id(sender, instance, created, **kwargs):
    if created and not instance.student_id:
        try:
            last_student = Student.objects.order_by('-id').first()
            if last_student and last_student.student_id:
                last_id_str = last_student.student_id.lstrip('S')
                if last_id_str.isdigit():
                    last_id = int(last_id_str)
                    new_id = f"S{str(last_id + 1).zfill(6)}"
                else:
                    new_id = f"S{str(last_student.id).zfill(6)}"
            else:
                new_id = "S000001"
            instance.student_id = new_id
            instance.save(update_fields=['student_id'])
        except Exception as e:
            instance.student_id = f"S{str(instance.id).zfill(6)}"
            instance.save(update_fields=['student_id'])








class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True) 

    def __str__(self):
        return self.name

class Profession(models.Model):
    title = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.title



class StudentDetail(models.Model):
    student = models.OneToOneField(
        Student, 
        on_delete=models.CASCADE,
        related_name='details',
        primary_key=True 
    )
    
    
    first_name = models.CharField(max_length=200, default="", blank=True)
    last_name = models.CharField(max_length=200, default="", blank=True)
    dob = models.DateField(null=True, blank=True, default=None)
    age = models.PositiveIntegerField()
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Male')
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=False, default="", blank=True)

    college = models.CharField(max_length=500, default="", blank=True)
    cgpa = models.FloatField(blank=True)
    batch = models.PositiveIntegerField()
    
    professions = models.ManyToManyField(Profession, related_name='students', blank=True)
    skills = models.ManyToManyField(Skill, related_name='students', blank=True)

    # fees = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    about = models.TextField(default="", blank=True)
    # availability_timings = models.CharField(max_length=50, default="#NA")
    profile_photo = models.URLField(max_length=900, null=True, blank=True, default=None)
    cv = models.TextField(max_length=1000, null=True, blank=True, default=None)

    is_approved = models.BooleanField()

    # total_students = models.PositiveIntegerField(default=0)
    total_sessions = models.PositiveIntegerField()
    # average_rating = models.FloatField(default=0.0)
    # years_of_experience = models.PositiveIntegerField(default=0)

    linkedin_url = models.CharField(max_length=250,blank=True, null=True)
    github_url = models.CharField(max_length=250,blank=True, null=True)
    portfolio_url = models.CharField(max_length=250,blank=True, null=True)

    def __str__(self):
        return f"{self.student.student_id} - {self.first_name} {self.last_name}"
    


class Booking(models.Model):
    student = models.ForeignKey('student.Student', on_delete=models.CASCADE, related_name="bookings")
    mentor = models.ForeignKey('mentor.Mentor', on_delete=models.CASCADE, related_name="bookings")
    subject = models.CharField(max_length=255)
    service = models.CharField(max_length=200, blank=True, null=True)  # Selected service title
    service_price = models.DecimalField(max_digits=10, decimal_places=2, default=80.00)  # Service price
    service_duration = models.CharField(max_length=50, default='60 min')  # Service duration
    time_slot = models.CharField(max_length=100)
    day = models.CharField(max_length=20, blank=True, null=True)  # Day of week (Monday, Tuesday, etc.)
    date = models.DateField(blank=True, null=True)  # Actual date of the booking
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'mentor', 'time_slot')

    def __str__(self):
        return f"Booking by {self.student.student_id} for {self.mentor.mentor_id}"





import uuid
from django.conf import settings
class StudentMessage(models.Model):
    message_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    # The receiver is always the student
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='received_messages'  # More descriptive
    )

    # The sender (mentor or admin)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_student_messages'  # Ensure uniqueness here
    )

    subject = models.CharField(max_length=400)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-sent_at']
        verbose_name = "Student Message"
        verbose_name_plural = "Student Messages"

    def __str__(self):
        return f"To {self.student.name}: {self.subject} (ID: {self.message_id})"

    def mark_as_read(self):
        self.is_read = True
        self.save(update_fields=['is_read'])



class StudentNote(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="notes")
    title = models.CharField(max_length=555)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.student_id} - {self.title}"



class Feedback(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='feedback_given'
    )
    mentor = models.ForeignKey(
        'mentor.Mentor',
        on_delete=models.CASCADE,
        related_name='feedback_received'
    )
    meeting = models.ForeignKey(
        'mentor.Meeting',
        on_delete=models.CASCADE,
        related_name='feedback',
        null=True,
        blank=True
    )
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        help_text="Rate your experience with the mentor"
    )
    feedback_text = models.TextField(
        help_text="Please share your experience and suggestions"
    )
    is_approved = models.BooleanField(
        default=False,
        help_text="Admin approval for feedback visibility"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Student Feedback"
        verbose_name_plural = "Student Feedback"
        unique_together = ('student', 'meeting')  # Ensures one feedback per student per meeting
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'meeting'],
                name='unique_student_meeting_feedback'
            )
        ]

    def __str__(self):
        return f"Feedback from {self.student.name} to {self.mentor.name} - {self.get_rating_display()}"

    def save(self, *args, **kwargs):
        # Update mentor's average rating when feedback is saved
        super().save(*args, **kwargs)
        self.update_mentor_rating()

    def update_mentor_rating(self):
        """Update mentor's average rating based on all feedback (approved or not)"""
        all_feedback = Feedback.objects.filter(mentor=self.mentor)
        if all_feedback.exists():
            avg_rating = all_feedback.aggregate(avg=models.Avg('rating'))['avg']
            mentor_detail = self.mentor.details
            mentor_detail.average_rating = round(avg_rating, 2)
            mentor_detail.save(update_fields=['average_rating'])