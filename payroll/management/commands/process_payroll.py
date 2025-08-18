# payroll/management/commands/process_payroll.py
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from decimal import Decimal as DEC

from payroll.models import PayrollPeriod, PayrollRun, Payslip
from payroll.services.payroll_engine import PayrollEngine


class Command(BaseCommand):
    help = "Process payroll for a given period (format: YYYY-MM)"

    def add_arguments(self, parser):
        parser.add_argument(
            "period",
            type=str,
            help="Payroll period in format YYYY-MM (e.g. 2025-08)",
        )

    def handle(self, *args, **options):
        period_key = options["period"]

        try:
            year, month = period_key.split("-")
            year = int(year)
            month = int(month)
        except ValueError:
            raise CommandError("Period must be in format YYYY-MM")

        # Get or create payroll period
        period, created = PayrollPeriod.objects.get_or_create(
            year=year,
            month=month,
            defaults={"start_date": timezone.datetime(year, month, 1),
                      "end_date": timezone.datetime(year, month, 28)}  # adjust for last day
        )

        if not created and period.closed:
            self.stdout.write(self.style.WARNING(
                f"Payroll period {period_key} is already closed."
            ))
            return

        # Create payroll run
        run = PayrollRun.objects.create(period=period, processed_at=timezone.now())

        engine = PayrollEngine()

        employees = period.get_employees() if hasattr(period, "get_employees") else []
        if not employees:
            from payroll.models import Employee
            employees = Employee.objects.filter(active=True)

        count = 0
        for emp in employees:
            payslip = engine.run(emp, period)
            Payslip.objects.create(
                run=run,
                employee=emp,
                period=period,
                gross=payslip["gross"],
                taxable=payslip["taxable"],
                tax=payslip["tax"],
                ssnit=payslip["ssnit"],
                net=payslip["net"],
                details=payslip,  # store breakdown as JSON if model has JSONField
            )
            count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Processed payroll for {count} employees in period {period_key}"
        ))
