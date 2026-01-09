import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="Resort Rental Yield Sensitivity",
    layout="wide"
)

st.title("🏕️ Resort Rental Yield – Sensitivity Analysis")

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
# Sidebar Inputs
# -------------------------------------------------
st.sidebar.header("Base Case Assumptions")

B = st.sidebar.slider("Number of Domes", 1, 30, 5)
C = st.sidebar.slider("Revenue per Day per Dome (₹)", 1000, 10000, 5250, step=250)
D = st.sidebar.slider("Booking Days / Month", 1, 10, 5)
F = st.sidebar.slider("Recapex Provision (%)", 0, 60, 30) / 100
I = st.sidebar.slider("Budget per Dome (₹)", 5_00_000, 40_00_000, 20_00_000, step=50_000)

# -------------------------------------------------
# Core Financial Logic
# -------------------------------------------------
def rental_yield(B, C, D, F, I):
    E = B * C * D * 12
    G = I * B * (1 + F)
    return (E / G) * 100

E = B * C * D * 12
G = I * B * (1 + F)
Y = rental_yield(B, C, D, F, I)

# -------------------------------------------------
# KPI Cards
# -------------------------------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Yearly Rent (₹)", format_inr(E))
col2.metric("Total Budget (₹)", format_inr(G))
col3.metric("Rental Yield (%)", f"{Y:.2f}")

st.divider()

# -------------------------------------------------
# Sensitivity Ranges (INTEGERS ONLY)
# -------------------------------------------------
B_range = np.arange(1, 31)
C_range = np.arange(2000, 10001, 500)
D_range = np.arange(1, 31)
F_range = np.arange(0, 61, 5) / 100
I_range = np.arange(5_00_000, 40_00_001, 5_00_000)

# -------------------------------------------------
# Compute Sensitivities
# -------------------------------------------------
yield_B = [rental_yield(b, C, D, F, I) for b in B_range]
yield_C = [rental_yield(B, c, D, F, I) for c in C_range]
yield_D = [rental_yield(B, C, d, F, I) for d in D_range]
yield_F = [rental_yield(B, C, D, f, I) for f in F_range]
yield_I = [rental_yield(B, C, D, F, i) for i in I_range]

# -------------------------------------------------
# Small Multiples (2 x 3)
# -------------------------------------------------
fig = make_subplots(
    rows=2, cols=3,
    subplot_titles=[
        "Yield vs Number of Domes",
        "Yield vs Revenue per Day",
        "Yield vs Booking Days / Month",
        "Yield vs Recapex %",
        "Yield vs Budget per Dome",
        ""
    ]
)

fig.add_trace(
    go.Scatter(
        x=B_range, y=yield_B, mode="lines",
        hovertemplate="Domes: %{x:.0f}<br>Yield: %{y:.2f}%<extra></extra>"
    ), row=1, col=1
)

fig.add_trace(
    go.Scatter(
        x=C_range, y=yield_C, mode="lines",
        hovertemplate="Revenue/Day: ₹%{x:,.0f}<br>Yield: %{y:.2f}%<extra></extra>"
    ), row=1, col=2
)

fig.add_trace(
    go.Scatter(
        x=D_range, y=yield_D, mode="lines",
        hovertemplate="Booking Days: %{x:.0f}<br>Yield: %{y:.2f}%<extra></extra>"
    ), row=1, col=3
)

fig.add_trace(
    go.Scatter(
        x=F_range * 100, y=yield_F, mode="lines",
        hovertemplate="Recapex: %{x:.0f}%<br>Yield: %{y:.2f}%<extra></extra>"
    ), row=2, col=1
)

fig.add_trace(
    go.Scatter(
        x=I_range / 100000, y=yield_I, mode="lines",
        hovertemplate="Budget/Dome: ₹%{x:.0f} Lacs<br>Yield: %{y:.2f}%<extra></extra>"
    ), row=2, col=2
)

# -------------------------------------------------
# Axis Formatting
# -------------------------------------------------
fig.update_xaxes(title_text="Domes", row=1, col=1, tickformat=",d")
fig.update_xaxes(title_text="Revenue per Day (₹)", row=1, col=2, tickformat=",d")
fig.update_xaxes(title_text="Booking Days", row=1, col=3, tickformat=",d")
fig.update_xaxes(title_text="Recapex (%)", row=2, col=1, tickformat=",d")
fig.update_xaxes(title_text="Budget per Dome (₹ Lacs)", row=2, col=2, tickformat=",d")

fig.update_yaxes(title_text="Rental Yield (%)", range=[0, 30])

fig.update_layout(
    height=720,
    showlegend=False,
    title_text="Rental Yield Sensitivity – Small Multiples",
    title_x=0.5
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------
# Insight Box
# -------------------------------------------------
st.info(
    "🔍 **Key Insights**\n"
    "- Rental yield is structurally independent of number of domes.\n"
    "- Booking days and revenue per day are the strongest drivers.\n"
    "- Higher recapex and over-capex reduce yield non-linearly."
)
