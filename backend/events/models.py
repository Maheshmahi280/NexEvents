from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """User profile to store role-based information"""
    ROLE_CHOICES = [
        ('Seeker', 'Event Seeker'),
        ('Organizer', 'Event Organizer'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Seeker')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"


# Signal to create UserProfile when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Event(models.Model):
    CATEGORY_CHOICES = [
        ('Tech', 'Technology'),
        ('Arts', 'Arts'),
        ('Sports', 'Sports'),
        ('Education', 'Education'),
    ]

    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    date_time = models.DateTimeField()
    location = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    cover_image = models.URLField(blank=True, null=True)
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    organiser = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organised_events', null=True, blank=True)
    interested_users = models.ManyToManyField(User, related_name='interested_events', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
