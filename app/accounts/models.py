from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('secretary', 'Secretary'),
        ('instructor', 'Instructor'),
        ('student', 'Student'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    remaining_hours = models.PositiveIntegerField(default=0)
    
    def get_absolute_url(self):
        return reverse('student_detail', args=[str(self.id)])
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='instructor_profile')
    specialization = models.CharField(max_length=100, blank=True, null=True)
    
    def get_absolute_url(self):
        return reverse('instructor_detail', args=[str(self.id)])
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"