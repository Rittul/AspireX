from django.contrib.auth.backends import BaseBackend
from student.models import Student
from mentor.models import Mentor, MentorToken

class MultiUserBackend(BaseBackend):
    def authenticate(self, request, student_id=None, mentor_id=None, password=None, **kwargs):
        try:
            if student_id:
                user = Student.objects.get(student_id=student_id)
            elif mentor_id:
                user = Mentor.objects.get(mentor_id=mentor_id)
            else:
                return None

            if user.check_password(password) and self.user_can_authenticate(user):
                return user
            return None
        except (Student.DoesNotExist, Mentor.DoesNotExist):
            return None

    def get_user(self, user_id):
        try:
            return Student.objects.get(pk=user_id)
        except Student.DoesNotExist:
            try:
                return Mentor.objects.get(pk=user_id)
            except Mentor.DoesNotExist:
                return None

    def user_can_authenticate(self, user):
        return getattr(user, 'is_active', True)