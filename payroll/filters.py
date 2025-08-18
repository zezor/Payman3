import django_filters
from .models import Employee, PayrollRecord


class EmployeeFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(lookup_expr="icontains")
    last_name = django_filters.CharFilter(lookup_expr="icontains")
    department = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Employee
        fields = ["first_name", "last_name", "department"]


class PayrollRecordFilter(django_filters.FilterSet):
    employee__first_name = django_filters.CharFilter(lookup_expr="icontains")
    employee__last_name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = PayrollRecord
        fields = ["employee", "period_start", "period_end"]
