from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
    ]
    PERIOD_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    # Holds the active SubscriptionPlan.slug (e.g. 'basic', 'pro', 'enterprise')
    # or 'free'. Denormalized from Subscription for fast tier checks.
    subscription_plan = models.CharField(max_length=50, default='free')
    subscription_start = models.DateTimeField(null=True, blank=True)
    subscription_end = models.DateTimeField(null=True, blank=True)
    subscription_period = models.CharField(max_length=10, choices=PERIOD_CHOICES, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.email} ({self.role})"

    @property
    def is_premium(self):
        from django.utils import timezone
        if not self.subscription_plan or self.subscription_plan == 'free':
            return False
        if self.subscription_end and self.subscription_end < timezone.now():
            return False
        return True

    @property
    def is_admin_user(self):
        return self.role == 'admin' or self.is_superuser
