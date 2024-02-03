from django.contrib.auth.backends import ModelBackend, UserModel
from django.contrib.auth.models import User
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Q


class PasswordlessAuthBackend(ModelBackend):
    """Log in to Django without providing a password."""

    def authenticate(self, username=None):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:  # to allow authentication through phone number or any other field, modify the below statement
            # print(username)
            # print([u.email for u in User.objects.all()])
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )

        except UserModel.DoesNotExist:
            # print("no user")
            UserModel().set_password(password)
        except MultipleObjectsReturned:
            # print("multiple objects")
            return User.objects.filter(email=username).order_by("id").first()
        else:
            # print(password, user.check_password(password))
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

    def get_user(self, user_id):
        try:
            user = UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None

        return user if self.user_can_authenticate(user) else None
