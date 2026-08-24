"""Time-value withdrawal calculator: drain account to $0 over N years."""
from __future__ import annotations

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="TVM Withdrawal Calculator",
    page_icon="💰",
    layout="centered",
)


def payment(pv: float, n: int, r: float) -> float:
    """Equal end-of-period withdrawal so balance hits ~0 after n periods."""
    if n <= 0:
        raise ValueError("n must be positive")
    if pv <= 0:
        raise ValueError("pv must be positive")
    if r < 0:
        raise ValueError("r must be non-negative")
    if r == 0:
        return pv / n
    growth = (1.0 + r) ** n
    return pv * (r * growth) / (growth - 1.0)


def schedule(pv: float, n: int, r: float, pmt: float) -> pd.DataFrame:
    bal = float(pv)
    rows = []
    for k in range(1, n + 1):
        interest = bal * r
        bal = bal + interest - pmt
        # clamp tiny float residue on last period
        if k == n and abs(bal) < 1e-6:
            bal = 0.0
        rows.append(
            {
                "Period": k,
                "Interest": interest,
                "Withdrawal": pmt,
                "Ending balance": bal,
            }
        )
    return pd.DataFrame(rows)


def money(x: float) -> str:
    return f"${x:,.2f}"


st.title("How much can I take out each year?")
st.write(
    "Given a starting balance, years, and market rate, this estimates the "
    "**constant withdrawal** that leaves the account at **$0** at the end."
)

col1, col2 = st.columns(2)
with col1:
    pv = st.number_input(
        "Starting balance ($)",
        min_value=0.0,
        value=500_000.0,
        step=10_000.0,
        format="%.2f",
    )
    years = st.number_input("Total years", min_value=1, value=30, step=1)
with col2:
    rate_pct = st.number_input(
        "Annual interest rate (%)",
        min_value=0.0,
        value=5.0,
        step=0.25,
        format="%.2f",
    )
    frequency = st.radio("Withdrawal frequency", ["Annual", "Monthly"], horizontal=True)

r_annual = rate_pct / 100.0

if pv <= 0:
    st.warning("Enter a starting balance greater than zero.")
    st.stop()

if frequency == "Annual":
    n = int(years)
    r = r_annual
    pmt = payment(pv, n, r)
    period_label = "per year"
    periods_per_year = 1
else:
    n = int(years) * 12
    r = r_annual / 12.0
    pmt = payment(pv, n, r)
    period_label = "per month"
    periods_per_year = 12

total_out = pmt * n
interest_earned = total_out - pv
annual_equiv = pmt * periods_per_year

st.divider()
m1, m2, m3 = st.columns(3)
m1.metric(f"You can withdraw {period_label}", money(pmt))
m2.metric("Total withdrawn", money(total_out))
m3.metric("Interest earned along the way", money(interest_earned))

if frequency == "Monthly":
    st.caption(f"That’s about **{money(annual_equiv)} per year** in withdrawals.")

st.info(
    "Assumptions: constant interest rate, withdrawals at the **end** of each period, "
    "and the balance is driven to zero after the last withdrawal. Taxes, fees, and "
    "sequence-of-returns risk are not modeled."
)

with st.expander("Period-by-period schedule", expanded=False):
    # For long monthly runs, show a yearly rollup to keep the table readable
    if frequency == "Monthly" and years > 15:
        bal = float(pv)
        yearly = []
        for y in range(1, int(years) + 1):
            interest_y = 0.0
            withdrawn_y = 0.0
            for _ in range(12):
                interest = bal * r
                bal = bal + interest - pmt
                interest_y += interest
                withdrawn_y += pmt
            if y == int(years) and abs(bal) < 1e-4:
                bal = 0.0
            yearly.append(
                {
                    "Year": y,
                    "Interest": interest_y,
                    "Withdrawals": withdrawn_y,
                    "Ending balance": bal,
                }
            )
        df = pd.DataFrame(yearly)
        st.caption("Monthly mode with long horizons: showing yearly rollup.")
    else:
        df = schedule(pv, n, r, pmt)

    show = df.copy()
    for col in show.columns:
        if col not in ("Period", "Year"):
            show[col] = show[col].map(lambda v: f"{v:,.2f}")
    st.dataframe(show, width='stretch', hide_index=True)

st.caption("Live on Streamlit Community Cloud · repo seanholt111/streamlit-starter")
