from django import forms
from .models import Employee, PayrollRecord


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            "first_name", "last_name", "email",
            "staff_id", "department", "position",
            "basic_salary", "bank_name", "bank_account_number"
        ]


class PayrollRecordForm(forms.ModelForm):
    class Meta:
        model = PayrollRecord
        fields = ["employee", "period_start", "period_end", "gross_salary", "tax", "net_salary"]
