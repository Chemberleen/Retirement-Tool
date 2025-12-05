# -*- coding: utf-8 -*-
"""
Created on Fri Dec  5 22:40:13 2025

@author: leeno
"""

import streamlit as st
import matplotlib.pyplot as plt


# ----------------------------------------------------------
# Simulation function
# ----------------------------------------------------------
def simulate_retirement(
    monthly_contribution,
    current_age,
    retirement_age,
    life_expectancy,
    current_savings,
    expected_return_acc,
    expected_return_ret,
    inflation_rate,
    yearly_withdrawal,
):
    years = list(range(current_age, life_expectancy + 1))
    wealth = []
    value = current_savings
    yearly_contribution = monthly_contribution * 12
    success = True
    failure_year = None

    for age in years:
        if age < retirement_age:
            value = value * (1 + expected_return_acc)
            value += yearly_contribution
        else:
            value = value * (1 + expected_return_ret)
            withdrawal_adj = yearly_withdrawal * (
                (1 + inflation_rate) ** (age - retirement_age)
            )
            value -= withdrawal_adj

            if value <= 0 and success:
                success = False
                failure_year = age
                value = 0

        wealth.append(value)

    return years, wealth, success, failure_year


# ----------------------------------------------------------
# Binary search helpers
# ----------------------------------------------------------
def retirement_success(
    monthly_contribution,
    current_age,
    retirement_age,
    life_expectancy,
    current_savings,
    expected_return_acc,
    expected_return_ret,
    inflation_rate,
    yearly_withdrawal,
):
    _, _, success, _ = simulate_retirement(
        monthly_contribution,
        current_age,
        retirement_age,
        life_expectancy,
        current_savings,
        expected_return_acc,
        expected_return_ret,
        inflation_rate,
        yearly_withdrawal,
    )
    return success


def find_required_monthly_contribution(
    current_age,
    retirement_age,
    life_expectancy,
    current_savings,
    expected_return_acc,
    expected_return_ret,
    inflation_rate,
    yearly_withdrawal,
):
    low = 0
    high = 1000

    # Expand search space if needed
    while not retirement_success(
        high,
        current_age,
        retirement_age,
        life_expectancy,
        current_savings,
        expected_return_acc,
        expected_return_ret,
        inflation_rate,
        yearly_withdrawal,
    ):
        high *= 2

    # Binary search
    for _ in range(40):
        mid = (low + high) / 2
        if retirement_success(
            mid,
            current_age,
            retirement_age,
            life_expectancy,
            current_savings,
            expected_return_acc,
            expected_return_ret,
            inflation_rate,
            yearly_withdrawal,
        ):
            high = mid
        else:
            low = mid

    return high


# ----------------------------------------------------------
# Streamlit UI
# ----------------------------------------------------------
st.title("💰 Retirement Planning Simulator & Calculator")
st.write(
    "Simulate your retirement or calculate the monthly investment required to retire safely."
)

# Sidebar
st.sidebar.header("Input Parameters")

current_age = st.sidebar.number_input("Current Age", 18, 80, 27)
retirement_age = st.sidebar.number_input(
    "Retirement Age", current_age + 1, 80, 65
)
life_expectancy = st.sidebar.number_input(
    "Life Expectancy", retirement_age + 1, 120, 90
)

current_savings = st.sidebar.number_input(
    "Current Savings (£)", 0, 1_000_000, 5000
)
monthly_contribution = st.sidebar.number_input(
    "Monthly Contribution (£)", 0, 5000, 300
)

expected_return_acc = (
    st.sidebar.slider("Return Before Retirement (%)", 0.0, 15.0, 7.0) / 100
)
expected_return_ret = (
    st.sidebar.slider("Return During Retirement (%)", 0.0, 10.0, 4.0) / 100
)

inflation_rate = st.sidebar.slider("Inflation Rate (%)", 0.0, 8.0, 2.0) / 100
yearly_withdrawal = st.sidebar.number_input(
    "Yearly Withdrawal (£)", 0, 100_000, 30000
)

mode = st.radio(
    "Choose Mode:",
    ["Simulate Retirement", "Calculate Required Monthly Contribution"],
)

# ----------------------------------------------------------
# Mode 1 — Simulation (with auto-calculation if failed)
# ----------------------------------------------------------
if mode == "Simulate Retirement":
    years, wealth, success, fail_year = simulate_retirement(
        monthly_contribution,
        current_age,
        retirement_age,
        life_expectancy,
        current_savings,
        expected_return_acc,
        expected_return_ret,
        inflation_rate,
        yearly_withdrawal,
    )

    # Plot
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(years, wealth)
    ax.set_xlabel("Age")
    ax.set_ylabel("Wealth (£)")
    ax.set_title("Retirement Wealth Projection")
    ax.grid(True)
    st.pyplot(fig)

    # Success or failure message
    if success:
        st.success(
            "✅ Your retirement plan is sustainable. You will not run out of money."
        )
    else:
        st.error(f"❌ Your money will run out at age **{fail_year}**.")
        st.info("🔄 Calculating how much you *should* invest instead...")

        # Auto-calc required contribution
        with st.spinner("Computing required monthly investment..."):
            required = find_required_monthly_contribution(
                current_age,
                retirement_age,
                life_expectancy,
                current_savings,
                expected_return_acc,
                expected_return_ret,
                inflation_rate,
                yearly_withdrawal,
            )

        st.warning(
            f"📌 To avoid running out of money, you need to invest **£{required:.2f}/month**"
        )


# ----------------------------------------------------------
# Mode 2 — Direct required monthly contribution calculator
# ----------------------------------------------------------
else:
    with st.spinner("Calculating required monthly contribution..."):
        required = find_required_monthly_contribution(
            current_age,
            retirement_age,
            life_expectancy,
            current_savings,
            expected_return_acc,
            expected_return_ret,
            inflation_rate,
            yearly_withdrawal,
        )

    st.subheader("Required Monthly Contribution")
    st.success(
        f"📌 You need to invest **£{required:.2f}/month** to retire safely at age {retirement_age}."
    )


st.write("---")
st.caption("Built with ❤️ using Streamlit")
