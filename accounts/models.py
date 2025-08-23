# accounts/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    ROLE_CHOICES = [
        ("admin", "System Administrator"),
        ("hr_manager", "HR Manager"),
        ("payroll_officer", "Payroll Officer"),
        ("auditor", "Auditor"),
        ("employee", "Employee"),
    ]

    email = models.EmailField(unique=True, blank=False) 
    department = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="employee")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # keeps username in superuser creation

    objects = UserManager()

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    


class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    employee_id = models.ForeignKey("payroll.Employee", on_delete=models.CASCADE, related_name="employee_profile")
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    bank_name = models.CharField(max_length=120, blank=True)
    bank_account_number = models.CharField(max_length=60, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.position} ({self.department})"