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
# Sidebar – COMMON INPUTS
# -------------------------------------------------
st.sidebar.header("Common Asset Assumptions")

B = st.sidebar.slider("Number of Domes", 1, 30, 5)
C = st.sidebar.slider("Revenue per Day per Dome (₹)", 1000, 10000, 5250, step=250)
F = st.sidebar.slider("Recapex Provision (%)", 0, 60, 30) / 100
I = st.sidebar.slider("Budget per Dome (₹)", 5_00_000, 40_00_000, 20_00_000, step=50_000)

Total_Budget = I * B * (1 + F)

# -------------------------------------------------
# Sidebar – LEASE INPUTS
# -------------------------------------------------
st.sidebar.header("Lease Contract Inputs")
D = st.sidebar.slider("Booking Days / Month", 1, 30, 5)

# -------------------------------------------------
# Sidebar – MANAGEMENT INPUTS
# -------------------------------------------------
st.sidebar.header("Management Contract Inputs")

occupancy = st.sidebar.slider("Occupancy (%)", 10, 100, 50) / 100
gross_margin = st.sidebar.slider("Gross Profit Margin (%)", 30, 80, 60) / 100
mgmt_fee = st.sidebar.slider("Management Fee (% of Revenue)", 5, 40, 20) / 100

net_margin = gross_margin - mgmt_fee

# -------------------------------------------------
# MODEL CALCULATIONS
# -------------------------------------------------
lease_revenue = B * C * D * 12
lease_yield = lease_revenue / Total_Budget * 100

mgmt_revenue = B * C * 30 * 12 * occupancy
net_profit = mgmt_revenue * net_margin
mgmt_yield = net_profit / Total_Budget * 100

# -------------------------------------------------
# CARD COLORS
# -------------------------------------------------
lease_color = "#e8f8f0" if lease_yield >= mgmt_yield else "#f4f4f4"
mgmt_color = "#e8f8f0" if mgmt_yield > lease_yield else "#f4f4f4"

# -------------------------------------------------
# SUMMARY CARDS
# -------------------------------------------------
st.markdown("## 📌 Contract Comparison")

c1, c2, c3 = st.columns([1, 2, 2])
c1.metric("Total Project Cost (₹)", format_inr(Total_Budget))

# ---------------- LEASE CARD ----------------
with c2:
    st.markdown(
        "<div style='background:{}; padding:18px; border-radius:12px'>"
        "<h3>📄 Lease Contract</h3>"
        "<h1>{:.2f}%</h1>"
        "<p><b>Annual Rent:</b> ₹ {}</p>"
        "</div>".format(lease_color, lease_yield, format_inr(lease_revenue)),
        unsafe_allow_html=True
    )

    with st.expander("How is this calculated?"):
        st.markdown(
            "**Annual Rent**  \n"
            "`{} × {} × {} × 12 = ₹ {}`  \n\n"
            "**Total Project Cost**  \n"
            "`{} × {} × (1 + {}%) = ₹ {}`  \n\n"
            "**Rental Yield**  \n"
            "`{} ÷ {} = {:.2f}%`  \n\n"
            "**Interpretation**  \n"
            "- Fixed & predictable income  \n"
            "- No operational risk  \n"
            "- Limited upside"
            .format(
                B, C, D, format_inr(lease_revenue),
                B, format_inr(I), int(F*100), format_inr(Total_Budget),
                format_inr(lease_revenue), format_inr(Total_Budget), lease_yield
            )
        )

# ---------------- MANAGEMENT CARD ----------------
with c3:
    st.markdown(
        "<div style='background:{}; padding:18px; border-radius:12px'>"
        "<h3>🏨 Management Contract</h3>"
        "<h1>{:.2f}%</h1>"
        "<p><b>Net Annual Profit:</b> ₹ {}</p>"
        "</div>".format(mgmt_color, mgmt_yield, format_inr(net_profit)),
        unsafe_allow_html=True
    )

    with st.expander("How is this calculated?"):
        st.markdown(
            "**Annual Revenue**  \n"
            "`{} × {} × 30 × 12 × {}% = ₹ {}`  \n\n"
            "**Net Margin**  \n"
            "`{}% − {}% = {}%`  \n\n"
            "**Net Profit**  \n"
            "`₹ {} × {}% = ₹ {}`  \n\n"
            "**Rental Yield**  \n"
            "`{} ÷ {} = {:.2f}%`  \n\n"
            "**Interpretation**  \n"
            "- Higher upside  \n"
            "- Operational risk  \n"
            "- Sensitive to occupancy & margins"
            .format(
                B, C, int(occupancy*100), format_inr(mgmt_revenue),
                int(gross_margin*100), int(mgmt_fee*100), int(net_margin*100),
                format_inr(mgmt_revenue), int(net_margin*100), format_inr(net_profit),
                format_inr(net_profit), format_inr(Total_Budget), mgmt_yield
            )
        )

# -------------------------------------------------
# DECISION MESSAGE
# -------------------------------------------------
if lease_yield > mgmt_yield:
    st.success("✅ Lease contract offers higher yield under current assumptions.")
elif mgmt_yield > lease_yield:
    st.success("✅ Management contract offers higher yield under current assumptions.")
else:
    st.info("ℹ️ Both contracts offer similar yields under current assumptions.")

# -------------------------------------------------
# SENSITIVITY ANALYSIS (LIGHT VERSION)
# -------------------------------------------------
st.divider()
st.markdown("## 🔁 Sensitivity Analysis")

# Lease – Booking Days
D_range = np.arange(1, 31)
yield_D = [(B * C * d * 12) / Total_Budget * 100 for d in D_range]

fig1 = make_subplots(rows=1, cols=1, subplot_titles=["Lease Yield vs Booking Days"])
fig1.add_trace(go.Scatter(x=D_range, y=yield_D))
fig1.update_yaxes(title_text="Rental Yield (%)", range=[0, 30])
st.plotly_chart(fig1, use_container_width=True)

# Management – Occupancy
occ_range = np.arange(20, 101, 5) / 100
y_occ = [(B * C * 30 * 12 * o * net_margin) / Total_Budget * 100 for o in occ_range]

fig2 = make_subplots(rows=1, cols=1, subplot_titles=["Management Yield vs Occupancy"])
fig2.add_trace(go.Scatter(x=occ_range * 100, y=y_occ))
fig2.update_yaxes(title_text="Rental Yield (%)", range=[0, 30])
st.plotly_chart(fig2, use_container_width=True)

# -------------------------------------------------
# DISCLAIMER
# -------------------------------------------------
st.caption(
    "Note: This model is for illustrative and comparative purposes only. "
    "Actual returns will depend on market conditions and execution."
)
