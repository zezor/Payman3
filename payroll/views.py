from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.urls import reverse
from django.core.paginator import Paginator
from accounts.decorators import role_required

from .models import PayrollPeriod
from .models import Employee, PayrollRecord
from .forms import EmployeeForm, PayrollRecordForm
from .filters import EmployeeFilter, PayrollRecordFilter



@role_required(["payroll_officer", "hr_manager", "admin"])
def employee_list(request):
    f = EmployeeFilter(request.GET, queryset=Employee.objects.all())
    paginator = Paginator(f.qs, 20)
    page = request.GET.get('page')
    employees = paginator.get_page(page)
    return render(request, "payroll/employee_list.html", {"filter": f, "employees": employees})


@role_required(["admin", "hr_manager"])
@permission_required("payroll.add_employee", raise_exception=True)
def employee_create(request):
 
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Employee added successfully.")
            return redirect("employee_list")
    else:
        messages.success(request, "Employee added successfully.")
        form = EmployeeForm()
    return render(request, "payroll/employee_form.html", {"form": form})

@role_required(["payroll_officer", "hr_manager", "admin"])
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    return render(request, "payroll/employee_detail.html", {"employee": employee})


@role_required(["admin", "hr_manager"])
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, "Employee updated successfully.")
            return redirect("employee_detail", pk=pk)
    else:
        form = EmployeeForm(instance=employee)
    return render(request, "payroll/employee_form.html", {"form": form})


@role_required(["payroll_officer", "hr_manager", "admin", "auditor"])
def payroll_list(request):
    f = PayrollRecordFilter(request.GET, queryset=PayrollRecord.objects.all())
    paginator = Paginator(f.qs, 20)
    page = request.GET.get('page')
    records = paginator.get_page(page)
    return render(request, "payroll/payroll_list.html", {"filter": f, "records": records})


@role_required(["payroll_officer", "hr_manager", "admin", "auditor"])
def payroll_detail(request, pk):
    record = get_object_or_404(PayrollRecord, pk=pk)
    return render(request, "payroll/payroll_detail.html", {"record": record})

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


def period_list(request):
    periods = PayrollPeriod.objects.all().order_by("-start_date")
    return render(request, "payroll/period_list.html", {"periods": periods})