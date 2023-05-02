"""
Models for Core App
"""
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)


class UserManager(BaseUserManager):
    """Manager for Users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save, and return a new user"""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user
    
    def create_superuser(self, email, password):
        """Create and return a new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user
    

class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Caverns(models.Model):
    """Cavern Setting Data"""
    name = models.CharField(max_length=255)
    gimp_file_ref = models.CharField(max_length=255)
    layer = models.IntegerField()
    found = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return f"{self.gimp_file_ref} - {self.name}"
    

class Links(models.Model):
    """Links between Caverns data."""
    name = models.CharField(max_length=255)
    travel_duration = models.CharField(max_length=255)
    caverns = models.ManyToManyField(Caverns)
    found = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return self.name