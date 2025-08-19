from django.urls import path
from .import views


app_name = "payroll"   # 👈 this line defines the namespace

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("employees/", views.employee_list, name="employee_list"),
    path("employee_create/", views.employee_create, name="employee_create"),
    path("employees/<int:pk>/", views.employee_detail, name="employee_detail"),
    path("employees/<int:pk>/edit/", views.employee_edit, name="employee_edit"),

    path("payroll/", views.payroll_list, name="payroll_list"),
    path("payroll/<int:pk>/", views.payroll_detail, name="payroll_detail"),

    path("periods/", views.period_list, name="period_list"),
]
