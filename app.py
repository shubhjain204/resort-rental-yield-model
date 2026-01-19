import streamlit as st
import numpy as np

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(page_title="Resort Yield Comparison", layout="wide")
st.title("🏕️ Resort Investment Model – Lease vs Management Contract")

# -------------------------------------------------
# Indian Number Formatter
# -------------------------------------------------
def format_inr(n):
    s = str(int(round(n)))
    if len(s) <= 3:
        return s
    last3 = s[-3:]
    rest = s[:-3]
    rest = ",".join([rest[max(i-2, 0):i] for i in range(len(rest), 0, -2)][::-1])
    return rest + "," + last3

# -------------------------------------------------
# Sidebar – Common Inputs
# -------------------------------------------------
st.sidebar.header("Common Asset Assumptions")

B = st.sidebar.slider("Number of Domes", 1, 30, 5)
C = st.sidebar.slider("Revenue per Day per Dome (₹)", 1000, 10000, 5250, step=250)
F = st.sidebar.slider("Recapex Provision (%)", 0, 60, 30) / 100
I = st.sidebar.slider("Budget per Dome (₹)", 5_00_000, 40_00_000, 20_00_000, step=50_000)

Total_Budget = I * B * (1 + F)

# -------------------------------------------------
# Lease Inputs
# -------------------------------------------------
st.sidebar.header("Lease Contract Inputs")
D = st.sidebar.slider("Booking Days / Month", 1, 30, 5)

# -------------------------------------------------
# Management Inputs
# -------------------------------------------------
st.sidebar.header("Management Contract Inputs")

occupancy = st.sidebar.slider("Occupancy (%)", 10, 100, 50) / 100
gross_margin = st.sidebar.slider("Gross Profit Margin (%)", 30, 80, 60) / 100
mgmt_fee = st.sidebar.slider("Management Fee (% of Revenue)", 5, 40, 20) / 100

net_margin = gross_margin - mgmt_fee

# -------------------------------------------------
# Base Calculations
# -------------------------------------------------
lease_revenue = B * C * D * 12
lease_yield = lease_revenue / Total_Budget * 100

mgmt_revenue = B * C * 30 * 12 * occupancy
net_profit = mgmt_revenue * net_margin
mgmt_yield = net_profit / Total_Budget * 100

# -------------------------------------------------
# Conditional Formatting
# -------------------------------------------------
lease_bg = "#e6f4ea" if lease_yield > mgmt_yield else "#f4f4f4"
mgmt_bg = "#e6f4ea" if mgmt_yield > lease_yield else "#f4f4f4"

# -------------------------------------------------
# Yield Cards
# -------------------------------------------------
st.markdown("## 📌 Contract Comparison")

c1, c2, c3 = st.columns([1, 2, 2])
c1.metric("Total Project Cost (₹)", format_inr(Total_Budget))

with c2:
    st.markdown(
        f"""
        <div style="background:{lease_bg}; padding:18px; border-radius:12px">
        <h4>📄 Lease Contract</h4>
        <h2>{lease_yield:.2f}%</h2>
        <p><b>Annual Rent:</b> ₹ {format_inr(lease_revenue)}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.expander("How is this calculated?"):
        st.markdown(
            f"""
Annual Rent = `{B} × {C} × {D} × 12`

Rental Yield = `{format_inr(lease_revenue)} ÷ {format_inr(Total_Budget)}`
"""
        )

with c3:
    st.markdown(
        f"""
        <div style="background:{mgmt_bg}; padding:18px; border-radius:12px">
        <h4>🏨 Management Contract</h4>
        <h2>{mgmt_yield:.2f}%</h2>
        <p><b>Net Annual Profit:</b> ₹ {format_inr(net_profit)}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.expander("How is this calculated?"):
        st.markdown(
            f"""
Annual Revenue = `{B} × {C} × 30 × 12 × {int(occupancy*100)}%`

Net Margin = `{int(gross_margin*100)}% − {int(mgmt_fee*100)}%`

Rental Yield = `{format_inr(net_profit)} ÷ {format_inr(Total_Budget)}`
"""
        )

# -------------------------------------------------
# 🔥 SENSITIVITY SUMMARY + DELTA CARDS
# -------------------------------------------------
st.divider()
st.markdown("## 🔥 Sensitivity Summary (What Really Matters)")

DELTA = 0.10  # 10% change

def lease_yield_with(delta_C=0, delta_D=0):
    rev = B * (C * (1 + delta_C)) * (D * (1 + delta_D)) * 12
    return rev / Total_Budget * 100

def mgmt_yield_with(delta_occ=0, delta_C=0, delta_margin=0):
    rev = B * (C * (1 + delta_C)) * 30 * 12 * (occupancy * (1 + delta_occ))
    margin = net_margin * (1 + delta_margin)
    return (rev * margin) / Total_Budget * 100

# Lease Sensitivities
lease_sens = {
    "Booking Days": lease_yield_with(delta_D=DELTA) - lease_yield,
    "Revenue / Day": lease_yield_with(delta_C=DELTA) - lease_yield,
}

# Management Sensitivities
mgmt_sens = {
    "Occupancy": mgmt_yield_with(delta_occ=DELTA) - mgmt_yield,
    "Revenue / Day": mgmt_yield_with(delta_C=DELTA) - mgmt_yield,
    "Net Margin": mgmt_yield_with(delta_margin=DELTA) - mgmt_yield,
}

# -------------------------------------------------
# Delta Cards
# -------------------------------------------------
st.markdown("### 📄 Lease Contract – Impact of +10% Change")

for k, v in lease_sens.items():
    st.metric(
        label=k,
        value=f"{v:+.2f}%",
        help="Change in rental yield for a +10% increase in this input"
    )

st.markdown("### 🏨 Management Contract – Impact of +10% Change")

for k, v in mgmt_sens.items():
    st.metric(
        label=k,
        value=f"{v:+.2f}%",
        help="Change in rental yield for a +10% increase in this input"
    )

# -------------------------------------------------
# Interpretation
# -------------------------------------------------
st.info(
    "💡 **How to use this:**\n"
    "- Inputs with larger delta have greater impact on returns\n"
    "- Lease model is most sensitive to demand (booking days)\n"
    "- Management model is most sensitive to execution (occupancy & margins)\n"
    "- Focus diligence on high-impact variables"
)

st.caption(
    "Note: Sensitivities are local and based on current assumptions. "
    "They indicate direction and relative importance, not forecasts."
)
