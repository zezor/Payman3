from django import forms
from .models import Employee, PayrollRecord


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            "first_name", "last_name", "email", "phone",
            "address", "id", "department", "position",
            "basic_salary", "bank_name", "bank_account_number"
        ]


class PayrollRecordForm(forms.ModelForm):
    class Meta:
        model = PayrollRecord
        fields = ["employee_id", "component_type", "description", "gross_salary", "net_salary"]
