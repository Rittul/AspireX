from typing import Optional, Tuple
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token as StudentToken
from mentor.models import MentorToken


class StudentOrMentorTokenAuthentication(BaseAuthentication):
    """Accept either DRF Token (Student) or MentorToken for Authorization: Token <key>."""

    keyword = b'token'

    def authenticate(self, request) -> Optional[Tuple[object, object]]:
        auth = get_authorization_header(request).split()

        if not auth:
            return None
        if auth[0].lower() != self.keyword:
            return None
        if len(auth) != 2:
            raise AuthenticationFailed('Invalid token header')

        try:
            key = auth[1].decode()
        except UnicodeError:
            raise AuthenticationFailed('Invalid token header')

        # Try Student token first
        try:
            token = StudentToken.objects.select_related('user').get(key=key)
            if not token.user.is_active:
                raise AuthenticationFailed('User inactive or deleted')
            return (token.user, token)
        except StudentToken.DoesNotExist:
            pass

        # Try Mentor token
        try:
            mtoken = MentorToken.objects.select_related('user').get(key=key)
            user = mtoken.user
            if not getattr(user, 'is_active', True):
                raise AuthenticationFailed('User inactive or deleted')
            return (user, mtoken)
        except MentorToken.DoesNotExist:
            raise AuthenticationFailed('Invalid token') 