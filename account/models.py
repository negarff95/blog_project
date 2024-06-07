import logging

from django.utils import timezone

from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.db import models

from core.models import BaseModel


class UserManager(BaseUserManager):
    """
    Custom user manager class to manage user creation
    """
    def _create_user(self, username, password, **extra_fields):
        """
        Method to create a user instance with provided username and password
        """
        if not username:
            raise ValueError("The given username must be set")
        username = self.model.normalize_username(username)
        user = self.model(username=username, **extra_fields)
        if password:
            user.set_password(password)
        user.save()
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username=username, password=password, **extra_fields)

    def create_staff(self, username, password=None, **extra_fields):
        """
        Method to create a staff user
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username=username, password=password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        """
        Method to create a superuser
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username=username, password=password, **extra_fields)


class User(AbstractBaseUser, BaseModel, PermissionsMixin):
    username = models.CharField(
        max_length=150,
        unique=True,
    )
    email = models.EmailField(null=True, blank=True)
    first_name = models.CharField(max_length=256, blank=True)
    last_name = models.CharField(max_length=256, blank=True)
    is_staff = models.BooleanField(default=False)
    rates_count = models.PositiveIntegerField(default=0)
    rate_weight = models.FloatField(default=0.1, validators=[MinValueValidator(0), MaxValueValidator(1)])
    total_rates_weight = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(1)])

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['password']

    def __str__(self):
        return f'{self.id}| {self.username}'

    def increase_rates_count(self, num=1):
        self.rates_count += num
        self.save()

    def increase_total_rates_weight(self, weight):
        """
        Method to increase the total rates weight for the user
        """
        self.total_rates_weight += weight
        self.save()
        logging.info(f"New weight after saving: {self.total_rates_weight}")

    @property
    def account_age(self):
        age = (timezone.now() - self.created_at).days
        return age

    @property
    def rate_quality(self):
        """
        Property to calculate average user's rates weight
        """
        if self.rates_count and self.total_rates_weight:
            return round(self.total_rates_weight / self.rates_count, 3)
        return None

    @property
    def account_weight(self):
        """
        Property to calculate the weight (validity) of the user's join date and user's total rates(activity in site)
        """
        new_account_age_days = 30
        bronze_rates_threshold = 10
        silver_rates_threshold = 40
        gold_rates_threshold = 70

        weight_new_account = 0.1
        weight_bronze_account = 0.2
        weight_silver_account = 0.5
        weight_gold_account = 0.7
        weight_platinum_account = 1.0

        if self.account_age < new_account_age_days:
            return weight_new_account
        if self.rates_count < bronze_rates_threshold:
            return weight_bronze_account
        elif self.rates_count < silver_rates_threshold:
            return weight_silver_account
        elif self.rates_count < gold_rates_threshold:
            return weight_gold_account
        else:
            return weight_platinum_account

    def calculate_rate_weight(self):
        """
        Method to calculate the rate weight of the user based on rate_quality and account_weight
        """
        account_weight_ratio = 1
        rate_quality_ratio = 1
        # if user has submitted rates
        if self.rate_quality:
            rate_weight = (
                ((account_weight_ratio * self.account_weight) +
                 (rate_quality_ratio * self.rate_quality)) /
                (rate_quality_ratio + account_weight_ratio)
            )
        else:  # if user has not submitted any rate
            rate_weight = self.account_weight
        self.rate_weight = round(rate_weight, 3)
        self.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
