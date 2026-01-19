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
# Calculations
# -------------------------------------------------
lease_revenue = B * C * D * 12
lease_yield = lease_revenue / Total_Budget * 100

mgmt_revenue = B * C * 30 * 12 * occupancy
net_profit = mgmt_revenue * net_margin
mgmt_yield = net_profit / Total_Budget * 100

# -------------------------------------------------
# Conditional Formatting Colors (RESTORED)
# -------------------------------------------------
lease_bg = "#e6f4ea" if lease_yield > mgmt_yield else "#f4f4f4"
mgmt_bg = "#e6f4ea" if mgmt_yield > lease_yield else "#f4f4f4"

# -------------------------------------------------
# Cards
# -------------------------------------------------
st.markdown("## 📌 Contract Comparison")

col1, col2, col3 = st.columns([1, 2, 2])
col1.metric("Total Project Cost (₹)", format_inr(Total_Budget))

# Lease Card
with col2:
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
**Annual Rent**  
`{B} × {C} × {D} × 12 = ₹ {format_inr(lease_revenue)}`

**Total Project Cost**  
`{B} × {format_inr(I)} × (1 + {int(F*100)}%) = ₹ {format_inr(Total_Budget)}`

**Rental Yield**  
`{format_inr(lease_revenue)} ÷ {format_inr(Total_Budget)} = {lease_yield:.2f}%`
"""
        )

# Management Card
with col3:
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
**Annual Revenue**  
`{B} × {C} × 30 × 12 × {int(occupancy*100)}% = ₹ {format_inr(mgmt_revenue)}`

**Net Margin**  
`{int(gross_margin*100)}% − {int(mgmt_fee*100)}% = {int(net_margin*100)}%`

**Net Profit**  
`₹ {format_inr(mgmt_revenue)} × {int(net_margin*100)}% = ₹ {format_inr(net_profit)}`

**Rental Yield**  
`{format_inr(net_profit)} ÷ {format_inr(Total_Budget)} = {mgmt_yield:.2f}%`
"""
        )

# -------------------------------------------------
# Sensitivity Analysis (UNCHANGED, STABLE)
# -------------------------------------------------
st.divider()
st.markdown("## 🔁 Sensitivity Analysis")

# Lease
st.markdown("### 📄 Lease Contract – Key Drivers")

D_range = np.arange(1, 31)
C_range = np.arange(2000, 10001, 500)
F_range = np.arange(0, 61, 5) / 100
I_range = np.arange(5_00_000, 40_00_001, 5_00_000)

yield_D = [(B * C * d * 12) / Total_Budget * 100 for d in D_range]
yield_C = [(B * c * D * 12) / Total_Budget * 100 for c in C_range]
yield_F = [(B * C * D * 12) / (I * B * (1 + f)) * 100 for f in F_range]
yield_I = [(B * C * D * 12) / (i * B * (1 + F)) * 100 for i in I_range]

fig_lease = make_subplots(
    rows=2, cols=2,
    subplot_titles=[
        "Yield vs Booking Days",
        "Yield vs Revenue / Day",
        "Yield vs Recapex %",
        "Yield vs Budget per Dome"
    ]
)

fig_lease.add_trace(go.Scatter(x=D_range, y=yield_D,
    hovertemplate="Booking Days: %{x}<br>Yield: %{y:.2f}%<extra></extra>"), 1, 1)
fig_lease.add_trace(go.Scatter(x=C_range, y=yield_C,
    hovertemplate="Revenue/Day: ₹%{x}<br>Yield: %{y:.2f}%<extra></extra>"), 1, 2)
fig_lease.add_trace(go.Scatter(x=F_range*100, y=yield_F,
    hovertemplate="Recapex: %{x}%<br>Yield: %{y:.2f}%<extra></extra>"), 2, 1)
fig_lease.add_trace(go.Scatter(x=I_range/100000, y=yield_I,
    hovertemplate="Budget/Dome: ₹%{x} Lacs<br>Yield: %{y:.2f}%<extra></extra>"), 2, 2)

fig_lease.update_yaxes(range=[0, 30])
fig_lease.update_layout(height=600, showlegend=False)
st.plotly_chart(fig_lease, use_container_width=True)

# Management
st.markdown("### 🏨 Management Contract – Key Drivers")

occ_range = np.arange(20, 101, 5) / 100
gross_range = np.arange(40, 81, 5) / 100
fee_range = np.arange(5, 41, 5) / 100

def mgmt_yield_calc(o, c, g, f, i):
    return (B * c * 30 * 12 * o * (g - f)) / (i * B * (1 + F)) * 100

y_occ = [mgmt_yield_calc(o, C, gross_margin, mgmt_fee, I) for o in occ_range]
y_rev = [mgmt_yield_calc(occupancy, c, gross_margin, mgmt_fee, I) for c in C_range]
y_gross = [mgmt_yield_calc(occupancy, C, g, mgmt_fee, I) for g in gross_range]
y_fee = [mgmt_yield_calc(occupancy, C, gross_margin, f, I) for f in fee_range]

fig_mgmt = make_subplots(
    rows=2, cols=2,
    subplot_titles=[
        "Yield vs Occupancy %",
        "Yield vs Revenue / Day",
        "Yield vs Gross Margin %",
        "Yield vs Management Fee %"
    ]
)

fig_mgmt.add_trace(go.Scatter(x=occ_range*100, y=y_occ,
    hovertemplate="Occupancy: %{x}%<br>Yield: %{y:.2f}%<extra></extra>"), 1, 1)
fig_mgmt.add_trace(go.Scatter(x=C_range, y=y_rev,
    hovertemplate="Revenue/Day: ₹%{x}<br>Yield: %{y:.2f}%<extra></extra>"), 1, 2)
fig_mgmt.add_trace(go.Scatter(x=gross_range*100, y=y_gross,
    hovertemplate="Gross Margin: %{x}%<br>Yield: %{y:.2f}%<extra></extra>"), 2, 1)
fig_mgmt.add_trace(go.Scatter(x=fee_range*100, y=y_fee,
    hovertemplate="Mgmt Fee: %{x}%<br>Yield: %{y:.2f}%<extra></extra>"), 2, 2)

fig_mgmt.update_yaxes(range=[0, 30])
fig_mgmt.update_layout(height=600, showlegend=False)
st.plotly_chart(fig_mgmt, use_container_width=True)

# -------------------------------------------------
# Disclaimer
# -------------------------------------------------
st.caption(
    "Note: This model is for illustrative and comparative purposes only. "
    "Actual returns depend on market conditions and execution."
)
