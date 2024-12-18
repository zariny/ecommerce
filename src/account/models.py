from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.utils import timezone
from core.models import ModelWithDescription


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, is_active=True, is_staff=False, is_superuser=False, **extra_fields)
        if password:
            user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        user = self.create_user(email, password, **extra_fields)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin, ModelWithDescription):
    email = models.EmailField("email address", unique=True, db_index=True)
    first_name = models.CharField("first name", max_length=150, blank=True, db_index=True)
    last_name = models.CharField("last name", max_length=150, blank=True, db_index=True)
    is_confirmed = models.BooleanField(default=False)
    is_staff = models.BooleanField(
        "staff status",
        default=False,
        help_text="Designates whether the user can log into this admin site."
    )
    is_active = models.BooleanField(
        "active",
        default=True,
        help_text=
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
    )
    date_joined = models.DateTimeField("date joined", default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    avatar = models.ImageField(upload_to="user-avatars", blank=True, null=True)
    language_code = models.CharField(max_length=35, choices=settings.CORE_LANGUAGES, default=settings.LANGUAGE_CODE)

    USERNAME_FIELD = "email"
    objects = UserManager()

    class Meta:
        app_label = "account"
        ordering = ("email",)

    def __str__(self):
        return self.full_name or self.email

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return "%s %s" % (self.first_name, self.last_name)
