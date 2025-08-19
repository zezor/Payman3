from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse
from django.core.paginator import Paginator
from accounts.decorators import role_required

from payroll.models import Employee, PayrollRecord


@role_required(["payroll_officer", "hr_manager", "admin", "auditor"])
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("login")
    
    # Example data for dashboard
    total_employees = Employee.objects.count()
    total_payroll_records = PayrollRecord.objects.count()
    
    return render(request, "payroll/dashboard.html", {
        "total_employees": total_employees,
        "total_payroll_records": total_payroll_records,
    })