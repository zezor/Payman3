from django import forms
from .models import Employee, PayrollRecord


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'  # Include all fields for the Employee model
        widgets = {
            "password": forms.PasswordInput(),
        }


class PayrollRecordForm(forms.ModelForm):
    class Meta:
        model = PayrollRecord
        fields = ["employee_id", "component_type", "description", "gross_salary", "net_salary"]
