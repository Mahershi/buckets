from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extrafields):
        if not email:
            raise ValueError("Email Must be Set!")
        if not password:
            raise ValueError("Password must be set!")

        user = self.model(email=email, **extrafields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password, **extrafields):
        extrafields.setdefault('is_superuser', True)
        extrafields.setdefault('is_staff', True)
        return self.create_user(email, password, **extrafields)