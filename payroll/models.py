from __future__ import annotations
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils import timezone

User = get_user_model()

class Department(models.Model):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

class GradeStep(models.Model):
    """Salary scale (e.g., Senior Lecturer: Grade SL, Step 3)."""
    title = models.CharField(max_length=120)   # e.g., Lecturer, Senior Lecturer, Admin Officer
    grade_code = models.CharField(max_length=20)  # e.g., SL
    step = models.PositiveIntegerField(default=1)
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ("grade_code", "step")
        ordering = ["grade_code", "step"]

    def __str__(self):
        return f"{self.title} ({self.grade_code}-{self.step})"

class Employee(models.Model):
    PERMANENT = "permanent"
    CONTRACT = "contract"
    ADJUNCT = "adjunct"
    EMPLOYMENT_TYPES = [
        (PERMANENT, "Permanent"),
        (CONTRACT, "Contract"),
        (ADJUNCT, "Adjunct"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employee")
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="employees")
    grade_step = models.ForeignKey(GradeStep, on_delete=models.PROTECT, related_name="employees")
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES, default=PERMANENT)
    bank_name = models.CharField(max_length=120, blank=True)
    bank_account_number = models.CharField(max_length=60, blank=True)
    email = models.EmailField(unique=True)
    position = models.CharField(max_length=100)
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    date_created = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.position} ({self.department})"



class AllowanceType(models.Model):
    """Catalog of allowance types (housing, transport, teaching, etc.)."""
    name = models.CharField(max_length=80, unique=True)
    is_taxable = models.BooleanField(default=True)
    is_percent_of_basic = models.BooleanField(default=False)
    percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # if percent-of-basic

    def __str__(self):
        return self.name

class DeductionType(models.Model):
    """Catalog of deduction types (loans, dues). Statutories handled separately."""
    name = models.CharField(max_length=80, unique=True)
    is_pre_tax = models.BooleanField(default=False)  # reduces taxable income if True

    def __str__(self):
        return self.name

class EmployeeAllowance(models.Model):
    employee_id = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="allowances")
    allowance_type = models.ForeignKey(AllowanceType, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("employee_id", "allowance_type")

class EmployeeDeduction(models.Model):
    employee_id = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="deductions")
    deduction_type = models.ForeignKey(DeductionType, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("employee_id", "deduction_type")

class TaxBracket(models.Model):
    """Generic progressive PAYE table for a given year and currency."""
    year = models.PositiveIntegerField()
    lower_bound = models.DecimalField(max_digits=12, decimal_places=2)
    upper_bound = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # None means infinity
    rate_percent = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        ordering = ["year", "lower_bound"]

    def __str__(self):
        ub = self.upper_bound if self.upper_bound is not None else "∞"
        return f"{self.year}: {self.lower_bound} – {ub} @ {self.rate_percent}%"

class StatutoryConfig(models.Model):
    """Statutory rates (e.g., social security). Versioned by effective date."""
    name = models.CharField(max_length=80)  # e.g., SSNIT Tier 1 (Employee)
    rate_percent = models.DecimalField(max_digits=5, decimal_places=2)
    effective_from = models.DateField(default=timezone.now)
    applies_to_employee = models.BooleanField(default=True)  # True: employee share; False: employer share

    class Meta:
        ordering = ["-effective_from", "name"]

    def __str__(self):
        who = "Employee" if self.applies_to_employee else "Employer"
        return f"{self.name} ({who}) {self.rate_percent}%"

class PayrollPeriod(models.Model):
    """Month-based period"""
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()  # 1–12
    is_closed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("year", "month")
        ordering = ["-year", "-month"]

    def __str__(self):
        return f"{self.year}-{self.month:02d}"

class PayrollRun(models.Model):
    DRAFT = "draft"
    APPROVED = "approved"
    PAID = "paid"
    STATUS = [(DRAFT, "Draft"), (APPROVED, "Approved"), (PAID, "Paid")]

    period = models.ForeignKey(PayrollPeriod, on_delete=models.PROTECT, related_name="runs")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="payroll_created")
    status = models.CharField(max_length=20, choices=STATUS, default=DRAFT)

    def __str__(self):
        return f"Run {self.id} – {self.period} ({self.status})"

class Payslip(models.Model):
    run = models.ForeignKey(PayrollRun, on_delete=models.CASCADE, related_name="payslips")
    employee_id = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="payslips")
    gross_pay = models.DecimalField(max_digits=12, decimal_places=2)
    taxable_income = models.DecimalField(max_digits=12, decimal_places=2)
    tax = models.DecimalField(max_digits=12, decimal_places=2)
    statutory_employee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    statutory_employer = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2)
    net_pay = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ("run", "employee_id")

class PayslipLine(models.Model):
    EARNING = "earning"
    DEDUCTION = "deduction"
    KIND = [(EARNING, "Earning"), (DEDUCTION, "Deduction")]

    payslip = models.ForeignKey(Payslip, on_delete=models.CASCADE, related_name="lines")
    kind = models.CharField(max_length=20, choices=KIND)
    label = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

class PayrollRecord(models.Model):
    """
    Stores each payroll line item (component) linked to a Payslip.
    Useful for audits, analytics, and exporting detailed payroll history.
    """
    payslip = models.ForeignKey("Payslip", on_delete=models.CASCADE, related_name="records")
    employee_id = models.ForeignKey("Employee", on_delete=models.CASCADE, related_name="payroll_records")

    COMPONENT_TYPES = [
        ("BASIC", "Basic Salary"),
        ("ALLOW", "Allowance"),
        ("DED", "Deduction"),
        ("SSNIT", "SSNIT"),
        ("PAYE", "PAYE Tax"),
        ("NET", "Net Pay"),
        ("OTHER", "Other"),
    ]
    component_type = models.CharField(max_length=10, choices=COMPONENT_TYPES)
    description = models.CharField(max_length=100, blank=True)
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2)
    tax = models.DecimalField(max_digits=12, decimal_places=2)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2)
    period_start = models.DateField()
    period_end = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["employee_id", "component_type"]

    def __str__(self):
        return f"{self.employee_id} - {self.component_type}: {self.amount}"
