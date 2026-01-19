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

# ---------- LEASE CARD ----------
with c2:
    st.markdown(
        f"""
        <div style="background:{lease_color}; padding:18px; border-radius:12px">
        <h3>📄 Lease Contract</h3>
        <h1>{lease_yield:.2f}%</h1>
        <p><b>Annual Rent:</b> ₹ {format_inr(lease_revenue)}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.expander("How is this calculated?"):
        st.markdown(f"""
**Annual Rent**
