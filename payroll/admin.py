from django.contrib import admin
from .models import Employee, PayrollPeriod, Department,GradeStep, AllowanceType,DeductionType ,PayrollRecord

# Register your models here.
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'department', 'position', 'basic_salary')
    search_fields = ('first_name', 'last_name', 'id')
    list_filter = ('department', 'position')

admin.site.register(Employee, EmployeeAdmin)

admin.site.register(PayrollPeriod)
admin.site.register(Department)
admin.site.register(GradeStep)
admin.site.register(AllowanceType)
admin.site.register(DeductionType)
admin.site.register(PayrollRecord)
