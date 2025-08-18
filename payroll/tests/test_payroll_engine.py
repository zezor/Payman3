# tests/test_payroll_engine.py
import pytest
from decimal import Decimal as DEC

from payroll.services.payroll_engine import PayrollEngine
from payroll.models import Employee, PayrollPeriod, Payslip


@pytest.mark.django_db
class TestPayrollEngine:
    def setup_method(self):
        # Create payroll period
        self.period = PayrollPeriod.objects.create(
            year=2025,
            month=8,
            start_date="2025-08-01",
            end_date="2025-08-31"
        )
        self.engine = PayrollEngine()

    def test_single_employee_run(self):
        emp = Employee.objects.create(
            first_name="John",
            last_name="Doe",
            basic_salary=DEC("5000.00"),
            allowances=DEC("1000.00"),
            active=True,
        )
        result = self.engine.run(emp, self.period)

        assert result["gross"] == DEC("6000.00")  # 5000 + 1000
        assert result["ssnit"] == DEC("660.00")   # 11% of gross
        expected_tax = (DEC("6000.00") - DEC("660.00")) * DEC("0.15")
        assert result["tax"] == expected_tax.quantize(DEC("0.01"))
        assert result["net"] == (result["gross"] - result["ssnit"] - result["tax"]).quantize(DEC("0.01"))

    def test_batch_run_multiple_employees(self):
        employees = [
            Employee.objects.create(first_name="Alice", last_name="Smith", basic_salary=DEC("3000.00"), allowances=DEC("500.00")),
            Employee.objects.create(first_name="Bob", last_name="Brown", basic_salary=DEC("4000.00"), allowances=DEC("800.00")),
            Employee.objects.create(first_name="Charlie", last_name="Johnson", basic_salary=DEC("2500.00"), allowances=DEC("300.00")),
        ]

        results = []
        for emp in employees:
            results.append(self.engine.run(emp, self.period))
            # Create payslip in DB
            Payslip.objects.create(
                employee=emp,
                period=self.period,
                gross=results[-1]["gross"],
                ssnit=results[-1]["ssnit"],
                tax=results[-1]["tax"],
                net=results[-1]["net"],
            )

        # Ensure payslips were created
        assert Payslip.objects.count() == 3

        # Validate one employee's payslip
        payslip = Payslip.objects.get(employee__first_name="Alice")
        assert payslip.gross == DEC("3500.00")  # 3000 + 500
        assert payslip.net == (payslip.gross - payslip.ssnit - payslip.tax).quantize(DEC("0.01"))

    def test_inactive_employee_skipped(self):
        emp = Employee.objects.create(
            first_name="Diana",
            last_name="Prince",
            basic_salary=DEC("4500.00"),
            allowances=DEC("700.00"),
            active=False,  # inactive employee
        )
        result = self.engine.run(emp, self.period)
        assert result is None  # engine should skip inactive employees
