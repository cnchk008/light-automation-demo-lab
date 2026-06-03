def calculate_payback_years(investment: float, annual_savings: float) -> float | None:
    if annual_savings <= 0:
        return None
    return investment / annual_savings


if __name__ == "__main__":
    investment = 120_000
    annual_labor_savings = 55_000
    annual_quality_savings = 10_000
    annual_maintenance_cost = 5_000

    net_annual_savings = (
        annual_labor_savings
        + annual_quality_savings
        - annual_maintenance_cost
    )

    payback = calculate_payback_years(investment, net_annual_savings)

    print(f"Investment: €{investment}")
    print(f"Net annual savings: €{net_annual_savings}")

    if payback is not None:
        print(f"Payback period: {payback:.2f} years")
    else:
        print("Payback cannot be calculated.")