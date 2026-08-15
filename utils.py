"""
Dhan Mitra — Calculation helpers standing in for Stations 1-4.
These recreate (in simplified form) the maths behind each earlier station,
so Station 5 has real, consistent numbers to personalise its coaching around.
"""
from config import INVESTMENT_ASSUMPTIONS, RISK_PROFILES


def compute_wellness_score(income: float, spends: dict) -> dict:
    """A simplified Financial Wellness Score (0-100), echoing Station 1."""
    total_spend = sum(spends.values())
    savings = max(income - total_spend, 0)
    savings_rate = (savings / income * 100) if income > 0 else 0

    # Score = savings-rate component (up to 60 pts) + spend-balance component (up to 40 pts)
    savings_component = min(savings_rate, 50) * 1.2
    if total_spend > 0:
        largest_share = max(spends.values()) / total_spend
        balance_component = max(0, 40 - largest_share * 100 * 0.4)
    else:
        balance_component = 40

    score = round(min(100, savings_component + balance_component))

    if score >= 80:
        band = "Excellent"
    elif score >= 60:
        band = "Good"
    elif score >= 40:
        band = "Needs Attention"
    else:
        band = "At Risk"

    return {
        "score": score,
        "band": band,
        "total_spend": total_spend,
        "savings": savings,
        "savings_rate": round(savings_rate, 1),
    }


def compute_goal_plan(target: float, saved: float, monthly: float, boost: float = 500) -> dict:
    """How many months to reach a goal — and a faster alternative, per Station 2."""
    remaining = max(target - saved, 0)
    months = remaining / monthly
    faster_months = remaining / (monthly + boost)
    return {
        "months": round(months, 1),
        "faster_months": round(faster_months, 1),
        "months_saved": round(months - faster_months, 1),
        "boost": boost,
    }


def compute_risk_score(answers: list) -> int:
    return sum(answers)


def compute_risk_profile(total_score: int) -> str:
    for (low, high), label in RISK_PROFILES.items():
        if low <= total_score <= high:
            return label
    return "Moderate"


def future_value_sip(monthly: float, years: float, annual_rate: float) -> float:
    """Future value of a monthly SIP with monthly compounding."""
    n = max(int(round(years * 12)), 0)
    r = annual_rate / 12
    if n == 0:
        return 0.0
    if r == 0:
        return monthly * n
    return monthly * (((1 + r) ** n - 1) / r) * (1 + r)


def investment_comparison(monthly: float, years: float) -> dict:
    """Projected value of the same monthly amount across FD / Gold / MF / Stocks."""
    return {
        name: round(future_value_sip(monthly, years, rate))
        for name, rate in INVESTMENT_ASSUMPTIONS.items()
    }


def compound_growth_series(monthly: float, years: int, annual_rate_pct: float) -> list:
    """Year-by-year projected corpus, for the Wealth Lab growth chart."""
    return [
        {"year": y, "value": round(future_value_sip(monthly, y, annual_rate_pct / 100))}
        for y in range(1, years + 1)
    ]
