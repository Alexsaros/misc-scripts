# financial_simulation.py
import matplotlib.pyplot as plt


def simulate_finances(
        start_capital: float,
        monthly_income: float,
        yearly_raise_percentage: float,
        monthly_costs: float,
        investment_ratio: float,
        investment_interest_yearly: float,
        inflation_rate_yearly: float = 0.03,
        capital_tax_yearly: float = 0.025,
        tax_free_capital: float = 57000,
        years: int = 50,
        # Home-related
        monthly_rent: float = 0.0,
        yearly_rent_increase: float = 0.0,
        home_value: float = 0.0,
        monthly_mortgage_payment: float = 0.0,
        mortgage_interest_rate: float = 0.0,
        hoa_monthly_fee: float = 0.0,
        yearly_home_appreciation: float = 0.06
):
    capital = start_capital
    income = monthly_income
    rent = monthly_rent

    monthly_inflation = (1 - inflation_rate_yearly) ** (1 / 12)
    investment_interest_monthly = (1 + investment_interest_yearly) ** (1/12) - 1
    monthly_home_appreciation = (1 + yearly_home_appreciation) ** (1/12) - 1
    monthly_mortgage_interest_rate = (1 + mortgage_interest_rate) ** (1/12) - 1

    months = years * 12

    interest_paid_this_year = 0
    remaining_principal = home_value

    # Track for graphing
    capital_history = []
    total_income_history = []
    monthly_costs_history = []

    for month in range(1, months + 1):
        # Add earned interest
        invested = capital * investment_ratio
        earned_interest = invested * investment_interest_monthly
        capital += earned_interest

        # Add income and subtract costs
        capital += income
        capital -= monthly_costs
        capital -= rent
        capital -= hoa_monthly_fee
        capital -= monthly_mortgage_payment

        interest = remaining_principal * monthly_mortgage_interest_rate
        principal_payment = monthly_mortgage_payment - interest
        remaining_principal -= principal_payment
        interest_paid_this_year += interest
        if remaining_principal < 0:
            remaining_principal = 0
            monthly_mortgage_payment = 0

        # Track monthly values
        total_income_history.append(earned_interest + income)
        monthly_costs_history.append(monthly_costs + rent + hoa_monthly_fee + monthly_mortgage_payment)

        if month % 12 == 0:
            # Calculate a raise
            income *= (1 + yearly_raise_percentage)

            # Rent increase
            rent *= (1 + yearly_rent_increase)

            # Calculate and apply tax
            taxable_capital = max(0, capital - tax_free_capital)
            capital -= taxable_capital * capital_tax_yearly

            # Mortgage interest refund (37.48% of yearly interest)
            refund = interest_paid_this_year * 0.3748
            capital += refund
            interest_paid_this_year = 0

            # Property tax on notional rental value
            notional_rental_value = home_value * 0.0035
            property_tax = notional_rental_value * 0.495
            capital -= property_tax

        # Apply inflation and appreciation
        capital *= monthly_inflation
        capital_history.append(capital)
        home_value *= (1 + monthly_home_appreciation)

    return round(capital, 2), total_income_history, monthly_costs_history
