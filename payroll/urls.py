from django.urls import path
from .import views

urlpatterns = [
    path("employees/", views.employee_list, name="employee_list"),
    path("employees/add/", views.employee_create, name="employee_create"),
    path("employees/<int:pk>/", views.employee_detail, name="employee_detail"),
    path("employees/<int:pk>/edit/", views.employee_edit, name="employee_edit"),

    path("payroll/", views.payroll_list, name="payroll_list"),
    path("payroll/<int:pk>/", views.payroll_detail, name="payroll_detail"),
]
