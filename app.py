import streamlit as st
import pandas as pd

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(page_title="Resort Yield Model", layout="wide")
st.title("🏕️ Resort Rental Yield – Lease vs Management")

# -------------------------------------------------
# Helpers
# -------------------------------------------------
def format_inr(n):
    n = int(round(n))
    s = str(n)
    if len(s) <= 3:
        return s
    last3 = s[-3:]
    rest = s[:-3]
    rest = ",".join([rest[max(i-2, 0):i] for i in range(len(rest), 0, -2)][::-1])
    return rest + "," + last3

def pct_change(new, base):
    return (new - base) / base * 100 if base != 0 else 0

# -------------------------------------------------
# Sidebar inputs
# -------------------------------------------------
st.sidebar.header("Common Inputs")

B = st.sidebar.slider("Number of Domes", 1, 30, 5)
C = st.sidebar.slider("Revenue per Day per Dome (₹)", 1000, 10000, 5250, step=250)
I = st.sidebar.slider("Budget per Dome (₹)", 5_00_000, 40_00_000, 20_00_000, step=50_000)
F = st.sidebar.slider("Recapex Provision (%)", 0, 60, 30) / 100

st.sidebar.header("Lease Model")
D = st.sidebar.slider("Booking Days / Month", 1, 30, 5)

st.sidebar.header("Management Model")
occupancy = st.sidebar.slider("Occupancy (%)", 10, 100, 50) / 100
mgmt_fee = st.sidebar.slider("Management Fee (% of Revenue)", 5, 40, 20) / 100
variable_cost = st.sidebar.slider("Variable Cost (% of Revenue)", 5, 30, 10) / 100
fixed_cost_pm = st.sidebar.slider(
    "Fixed Cost per Dome / Month (₹)", 5_000, 40_000, 15_000, step=1_000
)

# -------------------------------------------------
# Core calculations
# -------------------------------------------------
total_budget = I * B * (1 + F)

# Lease
lease_revenue = B * C * D * 12
lease_yield = lease_revenue / total_budget * 100

# Management
mgmt_revenue = B * C * 30 * 12 * occupancy
mgmt_fee_amt = mgmt_revenue * mgmt_fee
var_cost_amt = mgmt_revenue * variable_cost
fixed_cost_amt = fixed_cost_pm * B * 12

net_profit = mgmt_revenue - mgmt_fee_amt - var_cost_amt - fixed_cost_amt
mgmt_yield = net_profit / total_budget * 100

# -------------------------------------------------
# Cards
# -------------------------------------------------
st.markdown("## 📌 Contract Comparison")

c1, c2, c3 = st.columns([1, 2, 2])
c1.metric("Total Project Cost (₹)", format_inr(total_budget))

with c2:
    st.metric("Lease Yield", f"{lease_yield:.2f}%")
    with st.expander("How is this calculated?"):
        st.markdown(
            f"""
Annual Rent  
`{B} × {C} × {D} × 12 = ₹ {format_inr(lease_revenue)}`

Rental Yield  
`₹ {format_inr(lease_revenue)} ÷ ₹ {format_inr(total_budget)}`
"""
        )

with c3:
    st.metric("Management Yield", f"{mgmt_yield:.2f}%")
    with st.expander("How is this calculated?"):
        st.markdown(
            f"""
Annual Revenue  
`₹ {format_inr(mgmt_revenue)}`

Costs  
• Management Fee: ₹ {format_inr(mgmt_fee_amt)}  
• Variable Cost: ₹ {format_inr(var_cost_amt)}  
• Fixed Cost: ₹ {format_inr(fixed_cost_amt)}

Net Profit  
`₹ {format_inr(net_profit)}`

Rental Yield  
`₹ {format_inr(net_profit)} ÷ ₹ {format_inr(total_budget)}`
"""
        )

# -------------------------------------------------
# Sensitivity summary
# -------------------------------------------------
st.divider()
st.markdown("## 🔥 Sensitivity Summary (% change in yield for +10% input change)")

DELTA = 0.10
DELTA_SMALL = 0.01

def mgmt_yield_with(delta_occ=0, delta_fee=0, delta_fix=0):
    rev = B * C * 30 * 12 * (occupancy * (1 + delta_occ))
    fee = rev * (mgmt_fee * (1 + delta_fee))
    var = rev * variable_cost
    fixed = fixed_cost_pm * (1 + delta_fix) * B * 12
    profit = rev - fee - var - fixed
    return profit / total_budget * 100

rows = [
    ("Occupancy", pct_change(mgmt_yield_with(delta_occ=DELTA), mgmt_yield), "Execution risk"),
    ("Management Fee %", pct_change(mgmt_yield_with(delta_fee=DELTA), mgmt_yield), "Fee drag"),
    ("Fixed Cost / Dome", pct_change(mgmt_yield_with(delta_fix=DELTA), mgmt_yield), "Downside convexity"),
]

for name, sens, meaning in rows:

    c1, c2, c3, c4 = st.columns([2.5, 2, 3, 1])
    c1.markdown(f"**{name}**")
    c2.markdown(f"{sens:+.1f}%")
    c3.markdown(meaning)

    show = c4.button("🔍", key=name)

    if show:
        if name == "Occupancy":
            levels = [x / 100 for x in range(20, 101, 5)]
            elast = []
            for l in levels:
                base = mgmt_yield
                new = mgmt_yield_with(delta_occ=DELTA_SMALL)
                elast.append((new - base) / base / DELTA_SMALL)

            df = pd.DataFrame({
                "Occupancy (%)": [int(l * 100) for l in levels],
                "Elasticity": elast
            }).set_index("Occupancy (%)")

            st.line_chart(df)

        elif name == "Management Fee %":
            levels = [x / 100 for x in range(5, 41, 5)]
            elast = []
            for l in levels:
                base = mgmt_yield
                new = mgmt_yield_with(delta_fee=DELTA_SMALL)
                elast.append((new - base) / base / DELTA_SMALL)

            df = pd.DataFrame({
                "Mgmt Fee (%)": [int(l * 100) for l in levels],
                "Elasticity": elast
            }).set_index("Mgmt Fee (%)")

            st.line_chart(df)

        else:
            levels = list(range(5_000, 40_001, 5_000))
            elast = []
            for l in levels:
                base = mgmt_yield
                new = mgmt_yield_with(delta_fix=DELTA_SMALL)
                elast.append((new - base) / base / DELTA_SMALL)

            df = pd.DataFrame({
                "Fixed Cost / Month (₹000)": [int(l / 1000) for l in levels],
                "Elasticity": elast
            }).set_index("Fixed Cost / Month (₹000)")

            st.line_chart(df)

        st.caption("Elasticity = % change in yield for 1% change in this input")
        st.divider()
