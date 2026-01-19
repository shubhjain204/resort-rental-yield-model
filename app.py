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
# Yield Cards (RESTORED & STABLE)
# -------------------------------------------------
st.markdown("## 📌 Contract Comparison")

c1, c2, c3 = st.columns([1, 2, 2])
c1.metric("Total Project Cost (₹)", format_inr(Total_Budget))

# Lease Card
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
**Annual Rent**  
`{B} × {C} × {D} × 12 = ₹ {format_inr(lease_revenue)}`

**Total Project Cost**  
`{B} × {format_inr(I)} × (1 + {int(F*100)}%) = ₹ {format_inr(Total_Budget)}`

**Rental Yield**  
`{format_inr(lease_revenue)} ÷ {format_inr(Total_Budget)} = {lease_yield:.2f}%`
"""
        )

# Management Card
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
**Annual Revenue**  
`{B} × {C} × 30 × 12 × {int(occupancy*100)}% = ₹ {format_inr(mgmt_revenue)}`

**Gross Margin**  
`{int(gross_margin*100)}%`

**Management Fee**  
`{int(mgmt_fee*100)}%`

**Net Profit**  
`₹ {format_inr(mgmt_revenue)} × {int(net_margin*100)}% = ₹ {format_inr(net_profit)}`

**Rental Yield**  
`{format_inr(net_profit)} ÷ {format_inr(Total_Budget)} = {mgmt_yield:.2f}%`
"""
        )

# -------------------------------------------------
# 🔥 Sensitivity Summary Table
# -------------------------------------------------
st.divider()
st.markdown("## 🔥 Sensitivity Summary (What Impacts Rental Yield)")

DELTA = 0.10

def lease(delta_C=0, delta_D=0, delta_I=0, delta_F=0):
    rev = B * (C*(1+delta_C)) * (D*(1+delta_D)) * 12
    budget = (I*(1+delta_I)) * B * (1 + F*(1+delta_F))
    return rev / budget * 100

def mgmt(delta_C=0, delta_occ=0, delta_gm=0, delta_fee=0, delta_I=0, delta_F=0):
    rev = B * (C*(1+delta_C)) * 30 * 12 * (occupancy*(1+delta_occ))
    margin = (gross_margin*(1+delta_gm)) - (mgmt_fee*(1+delta_fee))
    budget = (I*(1+delta_I)) * B * (1 + F*(1+delta_F))
    return (rev * margin) / budget * 100

rows = [
    ("Revenue per Day",
     lease(delta_C=DELTA) - lease_yield,
     mgmt(delta_C=DELTA) - mgmt_yield,
     "Moves yield in same direction, moderate impact"),

    ("Booking Days",
     lease(delta_D=DELTA) - lease_yield,
     None,
     "Moves yield in same direction, strong impact"),

    ("Occupancy",
     None,
     mgmt(delta_occ=DELTA) - mgmt_yield,
     "Moves yield in same direction, strong impact"),

    ("Gross Margin",
     None,
     mgmt(delta_gm=DELTA) - mgmt_yield,
     "Strong impact – efficiency matters a lot"),

    ("Management Fee",
     None,
     mgmt(delta_fee=DELTA) - mgmt_yield,
     "Reduces yield – higher fee lowers returns"),

    ("Budget per Dome",
     lease(delta_I=DELTA) - lease_yield,
     mgmt(delta_I=DELTA) - mgmt_yield,
     "Reduces yield – capital heavy"),

    ("Recapex %",
     lease(delta_F=DELTA) - lease_yield,
     mgmt(delta_F=DELTA) - mgmt_yield,
     "Reduces yield gradually")
]

df = pd.DataFrame(rows, columns=[
    "Input",
    "Δ Yield – Lease (+10%)",
    "Δ Yield – Management (+10%)",
    "Relationship (Plain Language)"
])

df["Δ Yield – Lease (+10%)"] = df["Δ Yield – Lease (+10%)"].apply(
    lambda x: "—" if x is None else f"{x:+.2f}%"
)
df["Δ Yield – Management (+10%)"] = df["Δ Yield – Management (+10%)"].apply(
    lambda x: "—" if x is None else f"{x:+.2f}%"
)

st.dataframe(df, use_container_width=True)

st.caption(
    "Note: Sensitivities show how much rental yield changes for a ±10% change in each input, "
    "based on current assumptions."
)
