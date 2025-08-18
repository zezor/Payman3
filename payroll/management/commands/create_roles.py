# accounts/management/commands/create_roles.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = "Create default roles with permissions"

    def handle(self, *args, **kwargs):
        roles = ["admin", "hr_manager", "payroll_officer", "auditor", "employee"]
        for role in roles:
            group, created = Group.objects.get_or_create(name=role)
            self.stdout.write(self.style.SUCCESS(f"Role {role} ready."))
        self.stdout.write(self.style.SUCCESS("All roles created successfully."))