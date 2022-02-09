from django.db import models
from django.utils import timezone

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        
        user = self.create_user(
            email=email,
            password=password,
        )

        user.is_superuser = True
        user.save(using=self._db)
        return user

class QraftUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )

    date_joined = models.DateTimeField(
        verbose_name=('Date joined'),
        default=timezone.now
    )

    USERNAME_FIELD = 'email'
    objects = UserManager()