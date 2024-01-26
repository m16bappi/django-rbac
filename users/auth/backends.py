from django.utils import timezone
from django.contrib.auth.backends import ModelBackend
from rest_framework.exceptions import NotAuthenticated
from users.models import User, UserStatus, UserAccessTracks


MAX_ATTEMPTS = 5


class UserAuthModelBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None):
        try:
            user: User = User._default_manager.get_by_natural_key(email)
            self.access_tracks: UserAccessTracks = user.access_tracks
        except User.DoesNotExist:
            User().set_password(password)
        else:
            self._check_locked()
            if not user.check_password(password):
                self._update_tracks(request)
                self._attempts_left()

            self._check_restriction(user)
            self.access_tracks.reset_failed_attempts()

            return user

    def _update_tracks(self, request):
        self.access_tracks.failed_attempts += 1
        self.access_tracks.ip_address = request.META.get('REMOTE_ADDR')
        if self.access_tracks.failed_attempts >= MAX_ATTEMPTS:
            self.access_tracks.locked_at = timezone.now()
        self.access_tracks.save()

    def _check_locked(self):
        if self.access_tracks.locked_at:
            raise NotAuthenticated(
                f'Too many attempts taken, account locked at {self.access_tracks.locked_at}'
            )

    def _attempts_left(self):
        self._check_locked()

        left_attempts = MAX_ATTEMPTS - self.access_tracks.failed_attempts

        if left_attempts > 1:
            message = f'{left_attempts} attempts left'
        else:
            message = 'last attempt left'

        raise NotAuthenticated(
            f'Wrong password, {message}'
        )

    def _check_restriction(self, user: User):
        if user.status == UserStatus.BLOCKED:
            raise NotAuthenticated('account is blocked')
