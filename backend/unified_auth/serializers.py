from rest_framework import serializers
from django.contrib.auth import authenticate
from student.models import Student
from mentor.models import Mentor, MentorToken
from rest_framework.authtoken.models import Token
from student.serializers import StudentRegistrationSerializer
from mentor.serializers import MentorRegistrationSerializer

class UnifiedLoginSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=[('student', 'Student'), ('mentor', 'Mentor')])
    
    def validate(self, data):
        user_id = data.get('user_id')
        password = data.get('password')
        role = data.get('role')
        
        if not isinstance(password, str):
            raise serializers.ValidationError({"password": "Password must be a string."})
        
        if user_id and password and role:
            # Try to authenticate based on role
            if role == 'student':
                try:
                    user = Student.objects.get(student_id=user_id)
                    if user.check_password(password):
                        if not user.is_active:
                            raise serializers.ValidationError("User account is disabled.")
                        data['user'] = user
                        data['user_type'] = 'student'
                    else:
                        raise serializers.ValidationError("Unable to log in with provided credentials.")
                except Student.DoesNotExist:
                    raise serializers.ValidationError("Unable to log in with provided credentials.")
            elif role == 'mentor':
                try:
                    user = Mentor.objects.get(mentor_id=user_id)
                    if user.check_password(password):
                        if not user.is_active:
                            raise serializers.ValidationError("User account is disabled.")
                        data['user'] = user
                        data['user_type'] = 'mentor'
                    else:
                        raise serializers.ValidationError("Unable to log in with provided credentials.")
                except Mentor.DoesNotExist:
                    raise serializers.ValidationError("Unable to log in with provided credentials.")
        else:
            raise serializers.ValidationError("Must include 'user_id', 'password', and 'role'.")
        
        return data

class UnifiedRegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    role = serializers.ChoiceField(choices=[('student', 'Student'), ('mentor', 'Mentor')])
    accepted_terms = serializers.BooleanField(write_only=True, required=False, default=False)
    
    def validate_email(self, value):
        # Check if email already exists in either Student or Mentor models
        if Student.objects.filter(email=value).exists():
            raise serializers.ValidationError("A student with this email already exists.")
        if Mentor.objects.filter(email=value).exists():
            raise serializers.ValidationError("A mentor with this email already exists.")
        return value
    
    def create(self, validated_data):
        role = validated_data.pop('role')
        accepted_terms = validated_data.pop('accepted_terms', False)
        
        if role == 'student':
            # Use existing student registration logic
            student_data = {
                'name': validated_data['name'],
                'email': validated_data['email'],
                'password': validated_data['password'],
                'accepted_terms': accepted_terms,
            }
            student_serializer = StudentRegistrationSerializer(data=student_data)
            student_serializer.is_valid(raise_exception=True)
            student = student_serializer.save()
            return {'user': student, 'user_type': 'student'}
        else:
            # Use existing mentor registration logic
            mentor_data = {
                'name': validated_data['name'],
                'email': validated_data['email'],
                'password': validated_data['password'],
                'accepted_terms': accepted_terms,
            }
            mentor_serializer = MentorRegistrationSerializer(data=mentor_data)
            mentor_serializer.is_valid(raise_exception=True)
            mentor = mentor_serializer.save()
            return {'user': mentor, 'user_type': 'mentor'} 