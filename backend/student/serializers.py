from rest_framework import serializers
from django.contrib.auth import authenticate 
from mentor.models import Meeting
from .models import *


class StudentRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    accepted_terms = serializers.BooleanField(write_only=True)
    
    class Meta:
        model = Student
        fields = ('email', 'name', 'password', 'accepted_terms')
    
    def validate_password(self, value):
        from django.core.exceptions import ValidationError
        from django.contrib.auth.password_validation import validate_password
        if not isinstance(value, str):
            raise serializers.ValidationError("Password must be a string.")
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value
    
    def create(self, validated_data):
        accepted_terms = validated_data.pop('accepted_terms', False)
        student = Student.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password'],
            accepted_terms=accepted_terms
        )
        return student



class StudentLoginSerializer(serializers.Serializer):
    student_id = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        student_id = data.get('student_id')
        password = data.get('password')
        if not isinstance(password, str):
            raise serializers.ValidationError({"password": "Password must be a string."})
        if student_id and password:
            student = authenticate(student_id=student_id, password=password)
            if student:
                if not student.is_active:
                    raise serializers.ValidationError("User account is disabled.")
                data['student'] = student
            else:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
        else:
            raise serializers.ValidationError("Must include 'student_id' and 'password'.")
        return data
    

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ('name',)
    
    def to_internal_value(self, data):
        if isinstance(data, dict):
            name = data.get('name')
        else:
            name = data
        skill, _ = Skill.objects.get_or_create(name=name)
        return skill


class ProfessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession
        fields = ('title',)

    def to_internal_value(self, data):
        if isinstance(data, dict):
            title = data.get('title')
        else:
            title = data
        profession, _ = Profession.objects.get_or_create(title=title)
        return profession


class StudentDetailSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True)
    professions = ProfessionSerializer(many=True)

    class Meta:
        model = StudentDetail
        fields = (
            'first_name', 'last_name', 'dob', 'age', 'gender', 'email', 'phone_number',
            'college', 'cgpa', 'batch', 'professions', 'skills', 'about',
            'profile_photo', 'cv', 'is_approved',
            'linkedin_url', 'github_url', 'portfolio_url','total_sessions'
        )

from django.utils import timezone
from mentor.serializers import MeetingSerializer

class StudentMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentMessage
        fields = ['message_id', 'subject', 'message', 'sent_at', 'is_read', 'sender']


class StudentSerializer(serializers.ModelSerializer):
    details = StudentDetailSerializer()
    meetings = serializers.SerializerMethodField()
    messages = serializers.SerializerMethodField()
    class Meta:
        model = Student
        fields = ('student_id', 'email', 'name','details','meetings','messages')

    def get_meetings(self, obj):
        
        all_meetings = obj.mentor_meetings.all().order_by('scheduled_time')
        return MeetingSerializer(all_meetings, many=True).data
    

    def get_messages(self, obj):
        
        student_messages = obj.received_messages.all().order_by('-sent_at')
        return StudentMessageSerializer(student_messages, many=True).data

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', {})

        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        
        student_details = getattr(instance, 'details', None)
        if not student_details:
            from student.models import StudentDetail
            student_details = StudentDetail.objects.create(student=instance)
        skills_data = details_data.pop('skills', [])
        professions_data = details_data.pop('professions', [])

        
        for attr, value in details_data.items():
            setattr(student_details, attr, value)
        student_details.save()

        
        if skills_data:
            skill_objs = []
            for skill in skills_data:
                if isinstance(skill, Skill):
                    obj = skill
                else:
                    obj, _ = Skill.objects.get_or_create(name=skill.get('name'))
                skill_objs.append(obj)
            student_details.skills.set(skill_objs)


        if professions_data:
            profession_objs = []
            for prof in professions_data:
                if isinstance(prof, Profession):
                    obj = prof
                else:
                    obj, _ = Profession.objects.get_or_create(title=prof.get('title'))
                profession_objs.append(obj)
            student_details.professions.set(profession_objs)


        return instance


class MeetingSerializer(serializers.ModelSerializer):
    mentor_id = serializers.CharField(source='mentor.mentor_id', read_only=True)
    mentor_name = serializers.CharField(source='mentor.name', read_only=True)
    student_name = serializers.CharField(source='student.name', read_only=True)
    has_feedback = serializers.SerializerMethodField()
    
    class Meta:
        model = Meeting
        fields = ['meeting_id', 'title', 'scheduled_time', 'meeting_link', 'status', 'mentor_id', 'mentor_name', 'student_name', 'has_feedback']
    
    def get_has_feedback(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.feedback.filter(student=request.user).exists()
        return False
        

from rest_framework import serializers
from .models import Booking

class BookingSerializer(serializers.ModelSerializer):
    mentor_id = serializers.CharField(write_only=True)

    class Meta:
        model = Booking
        fields = ['mentor_id', 'subject', 'service', 'service_price', 'service_duration', 'time_slot', 'day', 'date', 'transaction_id', 'is_paid']

    def validate(self, data):
        request = self.context.get('request')
        student = request.user
        mentor_id = data.get('mentor_id')
        time_slot = data.get('time_slot')

        from mentor.models import Mentor
        try:
            mentor = Mentor.objects.get(mentor_id=mentor_id)
        except Mentor.DoesNotExist:
            raise serializers.ValidationError({"mentor_id": "Mentor with this ID does not exist."})

        if Booking.objects.filter(student=student, mentor=mentor, time_slot=time_slot).exists():
            raise serializers.ValidationError("This time slot has already been booked with this mentor.")
            
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        student = request.user 

        mentor_id = validated_data.pop('mentor_id')
        from mentor.models import Mentor
        mentor = Mentor.objects.get(mentor_id=mentor_id)

        booking = Booking.objects.create(student=student, mentor=mentor, **validated_data)
        return booking


class BookingListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing bookings (with day/date fields)
    """
    class Meta:
        model = Booking
        fields = ['id', 'subject', 'service', 'service_price', 'service_duration', 'time_slot', 'day', 'date', 'transaction_id', 'is_paid', 'created_at']


class StudentNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentNote
        fields = ['id', 'student', 'title', 'content', 'created_at']
        read_only_fields = ['id', 'created_at', 'student']

    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)


class FeedbackSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    mentor_name = serializers.CharField(source='mentor.name', read_only=True)
    meeting_title = serializers.CharField(source='meeting.title', read_only=True)
    mentor_id = serializers.CharField(write_only=True, required=False)
    meeting_id = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Feedback
        fields = [
            'id', 'student', 'mentor', 'meeting', 'rating', 'feedback_text',
            'is_approved', 'created_at', 'updated_at',
            'student_name', 'mentor_name', 'meeting_title', 'mentor_id', 'meeting_id'
        ]
        read_only_fields = ['student', 'is_approved', 'created_at', 'updated_at']
        extra_kwargs = {
            'mentor': {'required': False},
            'meeting': {'required': False}
        }

    def validate(self, data):
        mentor_id = data.pop('mentor_id', None)
        if mentor_id:
            from mentor.models import Mentor
            try:
                data['mentor'] = Mentor.objects.get(mentor_id=mentor_id)
            except Mentor.DoesNotExist:
                raise serializers.ValidationError({'mentor_id': 'Mentor not found'})

        meeting_id = data.pop('meeting_id', None)
        if meeting_id:
            from mentor.models import Meeting
            try:
                data['meeting'] = Meeting.objects.get(meeting_id=meeting_id)
            except Meeting.DoesNotExist:
                raise serializers.ValidationError({'meeting_id': 'Meeting not found'})

        
        student = self.context['request'].user
        meeting = data.get('meeting')
        if meeting:
            existing_feedback = Feedback.objects.filter(student=student, meeting=meeting)
            if existing_feedback.exists():
                raise serializers.ValidationError({
                    'meeting_id': 'You have already submitted feedback for this meeting.'
                })
        return data

    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)


class PublicStudentSerializer(serializers.ModelSerializer):
    details = StudentDetailSerializer()
    class Meta:
        model = Student
        fields = ('student_id', 'email', 'name', 'details')