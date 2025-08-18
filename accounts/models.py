# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ("admin", "System Administrator"),
        ("hr_manager", "HR Manager"),
        ("payroll_officer", "Payroll Officer"),
        ("auditor", "Auditor"),
        ("employee", "Employee"),
    ]
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(unique=True, blank=False) 
    department = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="employee")

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    

    REQUIRED_FIELDS = ['email']


class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    employee_id = models.CharField(max_length=30, unique=True)
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    bank_account_number = models.CharField(max_length=60, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.position} ({self.department})"