from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from payroll.models import (
    Employee, EmployeeAllowance, EmployeeDeduction,
    PayrollRun, PayrollPeriod, Payslip, PayslipLine,
    StatutoryConfig, TaxBracket
)

DEC = Decimal

@dataclass
class Result:
    gross: Decimal
    pre_tax_deductions: Decimal
    taxable_income: Decimal
    tax: Decimal
    statutory_employee: Decimal
    statutory_employer: Decimal
    other_deductions: Decimal
    net: Decimal

class PayrollEngine:
    def __init__(self, period: PayrollPeriod):
        self.period = period

    def _stat_rate(self, applies_to_employee=True) -> Decimal:
        cfg = (
            StatutoryConfig.objects
            .filter(effective_from__lte=timezone.now().date(), applies_to_employee=applies_to_employee)
            .order_by("-effective_from")
            .first()
        )
        return DEC(str(cfg.rate_percent)) / DEC("100") if cfg else DEC("0")

    def _calc_tax(self, year: int, taxable: Decimal) -> Decimal:
        brackets = TaxBracket.objects.filter(year=year).order_by("lower_bound")
        tax = DEC("0")
        remaining = taxable
        for b in brackets:
            lb = b.lower_bound
            ub = b.upper_bound if b.upper_bound is not None else taxable
            if remaining <= 0:
                break
            span = max(DEC("0"), min(remaining, ub - lb)) if b.upper_bound else remaining
            tax += span * (DEC(str(b.rate_percent)) / DEC("100"))
            remaining -= span
        return tax

    def compute_employee(self, emp: Employee) -> Result:
        basic = emp.grade_step.basic_salary
        # Earnings
        earnings = [basic]
        for al in emp.allowances.filter(active=True).select_related("allowance_type"):
            if al.allowance_type.is_percent_of_basic:
                amt = basic * (DEC(str(al.allowance_type.percent)) / DEC("100"))
            else:
                amt = al.amount
            earnings.append(amt)
        gross = sum(earnings, DEC("0"))

        # Deductions
        pre_tax = DEC("0.00")
        post_tax = DEC("0.00")

        for dd in emp.deductions.filter(active=True).select_related("deduction_type"):
            amount = dd.amount

            if dd.deduction_type.is_pre_tax:
                pre_tax += amount
            else:
                post_tax += amount
