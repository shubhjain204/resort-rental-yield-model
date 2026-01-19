import streamlit as st
import pandas as pd

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
# Sidebar – Inputs
# -------------------------------------------------
st.sidebar.header("Common Asset Assumptions")

B = st.sidebar.slider("Number of Domes", 1, 30, 5)
C = st.sidebar.slider("Revenue per Day per Dome (₹)", 1000, 10000, 5250, step=250)
F = st.sidebar.slider("Recapex Provision (%)", 0, 60, 30) / 100
I = st.sidebar.slider("Budget per Dome (₹)", 5_00_000, 40_00_000, 20_00_000, step=50_000)

st.sidebar.header("Lease Contract Inputs")
D = st.sidebar.slider("Booking Days / Month", 1, 30, 5)

st.sidebar.header("Management Contract Inputs")
occupancy = st.sidebar.slider("Occupancy (%)", 10, 100, 50) / 100
gross_margin = st.sidebar.slider("Gross Profit Margin (%)", 30, 80, 60) / 100
mgmt_fee = st.sidebar.slider("Management Fee (% of Revenue)", 5, 40, 20) / 100

net_margin = gross_margin - mgmt_fee
Total_Budget = I * B * (1 + F)

# -------------------------------------------------
# Base Yields
# -------------------------------------------------
lease_yield = (B * C * D * 12) / Total_Budget * 100
mgmt_yield = (B * C * 30 * 12 * occupancy * net_margin) / Total_Budget * 100

# -------------------------------------------------
# Yield Cards (unchanged)
# -------------------------------------------------
lease_bg = "#e6f4ea" if lease_yield > mgmt_yield else "#f4f4f4"
mgmt_bg = "#e6f4ea" if mgmt_yield > lease_yield else "#f4f4f4"

st.markdown("## 📌 Contract Comparison")

c1, c2, c3 = st.columns([1, 2, 2])
c1.metric("Total Project Cost (₹)", format_inr(Total_Budget))

with c2:
    st.markdown(
        f"<div style='background:{lease_bg}; padding:18px; border-radius:12px'>"
        f"<h4>📄 Lease Contract</h4><h2>{lease_yield:.2f}%</h2>"
        f"</div>", unsafe_allow_html=True
    )

with c3:
    st.markdown(
        f"<div style='background:{mgmt_bg}; padding:18px; border-radius:12px'>"
        f"<h4>🏨 Management Contract</h4><h2>{mgmt_yield:.2f}%</h2>"
        f"</div>", unsafe_allow_html=True
    )

# -------------------------------------------------
# 🔥 Sensitivity Summary Table
# -------------------------------------------------
st.divider()
st.markdown("## 🔥 Sensitivity Summary (Impact on Rental Yield)")
st.caption("Δ shows change in rental yield (percentage points) for a +10% change in input.")

DELTA = 0.10

def lease(delta_C=0, delta_D=0, delta_I=0, delta_F=0):
    rev = B * (C*(1+delta_C)) * (D*(1+delta_D)) * 12
    budget = (I*(1+delta_I)) * B * (1 + F*(1+delta_F))
    return rev / budget * 100

def mgmt(delta_C=0, delta_occ=0, delta_margin=0, delta_I=0, delta_F=0):
    rev = B * (C*(1+delta_C)) * 30 * 12 * (occupancy*(1+delta_occ))
    budget = (I*(1+delta_I)) * B * (1 + F*(1+delta_F))
    return (rev * (net_margin*(1+delta_margin))) / budget * 100

data = [
    ("Revenue / Day", 
     lease(delta_C=DELTA) - lease_yield,
     mgmt(delta_C=DELTA) - mgmt_yield,
     "Direct & proportional (pricing power)"),

    ("Booking Days",
     lease(delta_D=DELTA) - lease_yield,
     None,
     "Direct & proportional (demand-driven)"),

    ("Occupancy",
     None,
     mgmt(delta_occ=DELTA) - mgmt_yield,
     "Direct & proportional (execution-driven)"),

    ("Net Margin",
     None,
     mgmt(delta_margin=DELTA) - mgmt_yield,
     "Amplified (margin effect)"),

    ("Budget per Dome",
     lease(delta_I=DELTA) - lease_yield,
     mgmt(delta_I=DELTA) - mgmt_yield,
     "Inverse & dampening (capital intensity)"),

    ("Recapex %",
     lease(delta_F=DELTA) - lease_yield,
     mgmt(delta_F=DELTA) - mgmt_yield,
     "Inverse & dampening (long-term cost drag)")
]

df = pd.DataFrame(data, columns=[
    "Input",
    "Δ Yield – Lease (+10%)",
    "Δ Yield – Management (+10%)",
    "Relationship Type"
])

df["Δ Yield – Lease (+10%)"] = df["Δ Yield – Lease (+10%)"].apply(
    lambda x: "—" if x is None else f"{x:+.2f}%"
)
df["Δ Yield – Management (+10%)"] = df["Δ Yield – Management (+10%)"].apply(
    lambda x: "—" if x is None else f"{x:+.2f}%"
)

st.dataframe(df, use_container_width=True)

st.info(
    "💡 **How to read this table:**\n"
    "- Larger absolute Δ means higher sensitivity\n"
    "- Direct relationships scale predictably\n"
    "- Margin variables amplify upside & downside\n"
    "- Capital variables reduce yield gradually"
)

st.caption(
    "Note: Sensitivities are local (±10%) around current assumptions. "
    "They indicate relative importance, not forecasts."
)
