import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
# Sidebar – COMMON INPUTS (Asset-Level)
# -------------------------------------------------
st.sidebar.header("Common Asset Assumptions")

B = st.sidebar.slider("Number of Domes", 1, 30, 5)
C = st.sidebar.slider("Revenue per Day per Dome (₹)", 1000, 10000, 5250, step=250)
F = st.sidebar.slider("Recapex Provision (%)", 0, 60, 30) / 100
I = st.sidebar.slider("Budget per Dome (₹)", 5_00_000, 40_00_000, 20_00_000, step=50_000)

Total_Budget = I * B * (1 + F)

# -------------------------------------------------
# Sidebar – LEASE CONTRACT INPUTS
# -------------------------------------------------
st.sidebar.header("Lease Contract Inputs")

D = st.sidebar.slider("Booking Days / Month", 1, 30, 5)

# -------------------------------------------------
# Sidebar – MANAGEMENT CONTRACT INPUTS
# -------------------------------------------------
st.sidebar.header("Management Contract Inputs")

occupancy = st.sidebar.slider("Occupancy (%)", 10, 100, 50) / 100
gross_margin = st.sidebar.slider("Gross Profit Margin (%)", 30, 80, 60) / 100
mgmt_fee = st.sidebar.slider("Management Fee (% of Revenue)", 5, 40, 20) / 100

net_margin = gross_margin - mgmt_fee

# -------------------------------------------------
# MODEL CALCULATIONS
# -------------------------------------------------

# Lease Model
lease_revenue = B * C * D * 12
lease_yield = (lease_revenue / Total_Budget) * 100

# Management Model
mgmt_revenue = B * C * 30 * 12 * occupancy
net_profit = mgmt_revenue * net_margin
mgmt_yield = (net_profit / Total_Budget) * 100

# -------------------------------------------------
# CONDITIONAL HIGHLIGHTING
# -------------------------------------------------
lease_color = "#d4f8d4" if lease_yield > mgmt_yield else "#f2f2f2"
mgmt_color = "#d4f8d4" if mgmt_yield > lease_yield else "#f2f2f2"

# -------------------------------------------------
# KPI COMPARISON
# -------------------------------------------------
st.markdown("## 📌 Contract Comparison Summary")

c1, c2, c3 = st.columns(3)

c1.metric("Total Project Cost (₹)", format_inr(Total_Budget))

c2.markdown(
    f"""
    <div style="background:{lease_color}; padding:16px; border-radius:10px">
    <h4>Lease Contract</h4>
    <h2>{lease_yield:.2f}%</h2>
    <p>Annual Rent: ₹ {format_inr(lease_revenue)}</p>
    </div>
    """,
    unsafe_allow_html=True
)

c3.markdown(
    f"""
    <div style="background:{mgmt_color}; padding:16px; border-radius:10px">
    <h4>Management Contract</h4>
    <h2>{mgmt_yield:.2f}%</h2>
    <p>Net Annual Profit: ₹ {format_inr(net_profit)}</p>
    </div>
    """,
    unsafe_allow_html=True
)

if lease_yield > mgmt_yield:
    st.success("✅ Under current assumptions, **Lease Contract delivers higher rental yield**.")
elif mgmt_yield > lease_yield:
    st.success("✅ Under current assumptions, **Management Contract delivers higher rental yield**.")
else:
    st.info("ℹ️ Both contracts deliver similar rental yield under current assumptions.")

st.divider()

# -------------------------------------------------
# SENSITIVITY ANALYSIS
# -------------------------------------------------
st.markdown("## 🔁 Sensitivity Analysis by Contract Type")
st.caption(
    "Common asset assumptions apply to both models. "
    "The sections below show how contract-specific variables impact rental yield."
)

# -------------------------------------------------
# LEASE – SMALL MULTIPLES
# -------------------------------------------------
st.markdown("### 📄 Lease Contract – Model-Specific Drivers")
st.caption("These variables affect yield only under a lease contract.")

D_range = np.arange(1, 31)
C_range = np.arange(2000, 10001, 500)
I_range = np.arange(5_00_000, 40_00_001, 5_00_000)
F_range = np.arange(0, 61, 5) / 100

yield_D = [(B * C * d * 12) / Total_Budget * 100 for d in D_range]
yield_C = [(B * c * D * 12) / Total_Budget * 100 for c in C_range]
yield_I = [(B * C * D * 12) / (i * B * (1 + F)) * 100 for i in I_range]
yield_F = [(B * C * D * 12) / (I * B * (1 + f)) * 100 for f in F_range]

fig_lease = make_subplots(
    rows=2, cols=3,
    subplot_titles=[
        "Yield vs Booking Days",
        "Yield vs Revenue / Day",
        "Yield vs Recapex %",
        "Yield vs Budget per Dome",
        "",
        ""
    ]
)

fig_lease.add_trace(go.Scatter(x=D_range, y=yield_D), row=1, col=1)
fig_lease.add_trace(go.Scatter(x=C_range, y=yield_C), row=1, col=2)
fig_lease.add_trace(go.Scatter(x=F_range * 100, y=yield_F), row=1, col=3)
fig_lease.add_trace(go.Scatter(x=I_range / 100000, y=yield_I), row=2, col=1)

fig_lease.update_yaxes(title_text="Rental Yield (%)", range=[0, 30])
fig_lease.update_layout(height=650, showlegend=False)

st.plotly_chart(fig_lease, use_container_width=True)

# -------------------------------------------------
# MANAGEMENT – SMALL MULTIPLES
# -------------------------------------------------
st.markdown("### 🏨 Management Contract – Model-Specific Drivers")
st.caption(
    "These variables affect yield only under a management contract "
    "and represent operational risk and upside."
)

occ_range = np.arange(20, 101, 5) / 100
gross_range = np.arange(40, 81, 5) / 100
fee_range = np.arange(5, 41, 5) / 100

def mgmt_yield_calc(occ, c, gross, fee, i):
    revenue = B * c * 30 * 12 * occ
    net = revenue * (gross - fee)
    return net / (i * B * (1 + F)) * 100

y_occ = [mgmt_yield_calc(o, C, gross_margin, mgmt_fee, I) for o in occ_range]
y_rev = [mgmt_yield_calc(occupancy, c, gross_margin, mgmt_fee, I) for c in C_range]
y_gross = [mgmt_yield_calc(occupancy, C, g, mgmt_fee, I) for g in gross_range]
y_fee = [mgmt_yield_calc(occupancy, C, gross_margin, f, I) for f in fee_range]
y_capex = [mgmt_yield_calc(occupancy, C, gross_margin, mgmt_fee, i) for i in I_range]

fig_mgmt = make_subplots(
    rows=2, cols=3,
    subplot_titles=[
        "Yield vs Occupancy %",
        "Yield vs Revenue / Day",
        "Yield vs Gross Margin %",
        "Yield vs Management Fee %",
        "Yield vs Budget per Dome",
        ""
    ]
)

fig_mgmt.add_trace(go.Scatter(x=occ_range * 100, y=y_occ), row=1, col=1)
fig_mgmt.add_trace(go.Scatter(x=C_range, y=y_rev), row=1, col=2)
fig_mgmt.add_trace(go.Scatter(x=gross_range * 100, y=y_gross), row=1, col=3)
fig_mgmt.add_trace(go.Scatter(x=fee_range * 100, y=y_fee), row=2, col=1)
fig_mgmt.add_trace(go.Scatter(x=I_range / 100000, y=y_capex), row=2, col=2)

fig_mgmt.update_yaxes(title_text="Rental Yield (%)", range=[0, 30])
fig_mgmt.update_layout(height=650, showlegend=False)

st.plotly_chart(fig_mgmt, use_container_width=True)
