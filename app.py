import streamlit as st

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
mgmt_fee = st.sidebar.slider("Management Fee (% of Revenue)", 5, 40, 20) / 100
variable_cost = st.sidebar.slider("Variable Cost (% of Revenue)", 5, 30, 10) / 100
fixed_cost_per_dome = st.sidebar.slider(
    "Fixed Cost per Dome / Month (₹)", 5_000, 40_000, 15_000, step=1_000
)

Total_Budget = I * B * (1 + F)

# -------------------------------------------------
# Lease Model
# -------------------------------------------------
lease_revenue = B * C * D * 12
lease_yield = lease_revenue / Total_Budget * 100

# -------------------------------------------------
# Management Model
# -------------------------------------------------
mgmt_revenue = B * C * 30 * 12 * occupancy
mgmt_fee_amt = mgmt_revenue * mgmt_fee
variable_cost_amt = mgmt_revenue * variable_cost
fixed_cost_amt = fixed_cost_per_dome * B * 12

net_profit = mgmt_revenue - mgmt_fee_amt - variable_cost_amt - fixed_cost_amt
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

# -------------------------------------------------
# Sensitivity + Inline Elasticity
# -------------------------------------------------
st.divider()
st.markdown("## 🔥 Sensitivity Summary")

DELTA = 0.10
DELTA_SMALL = 0.01

def pct_change(new, base):
    return (new - base) / base * 100 if base != 0 else 0

def mgmt(delta_occ=0, delta_fee=0, delta_var=0, delta_fix=0):
    rev = B * C * 30 * 12 * (occupancy * (1 + delta_occ))
    fee_cost = rev * (mgmt_fee * (1 + delta_fee))
    var_cost = rev * (variable_cost * (1 + delta_var))
    fixed_cost = fixed_cost_per_dome * (1 + delta_fix) * B * 12
    profit = rev - fee_cost - var_cost - fixed_cost
    return profit / Total_Budget * 100

def elasticity(new, base):
    return (new - base) / base / DELTA_SMALL if base != 0 else 0

drivers = [
    ("Occupancy", "Execution driver", "occ"),
    ("Management Fee %", "Profit drag", "fee"),
    ("Variable Cost %", "Operating efficiency", "var"),
    ("Fixed Cost / Dome", "Downside convexity", "fix"),
]

for name, meaning, key in drivers:

    c1, c2, c3, c4 = st.columns([2.5, 2, 3, 1])
    c1.markdown(f"**{name}**")

    if key == "occ":
        sens = pct_change(mgmt(delta_occ=DELTA), mgmt_yield)
    elif key == "fee":
        sens = pct_change(mgmt(delta_fee=DELTA), mgmt_yield)
    elif key == "var":
        sens = pct_change(mgmt(delta_var=DELTA), mgmt_yield)
    else:
        sens = pct_change(mgmt(delta_fix=DELTA), mgmt_yield)

    c2.markdown(f"{sens:+.1f}%")
    c3.markdown(meaning)

    show = c4.button("🔍", key=name)

    if show:
        if key == "occ":
            xs = [x / 100 for x in range(20, 101, 5)]
            ys = [elasticity(mgmt(delta_occ=DELTA_SMALL), mgmt_yield)] * len(xs)
            st.line_chart({"Elasticity": ys}, x=[int(x * 100) for x in xs])

        elif key == "fee":
            xs = [x / 100 for x in range(5, 41, 5)]
            ys = [elasticity(mgmt(delta_fee=DELTA_SMALL), mgmt_yield)] * len(xs)
            st.line_chart({"Elasticity": ys}, x=[int(x * 100) for x in xs])

        elif key == "var":
            xs = [x / 100 for x in range(5, 31, 5)]
            ys = [elasticity(mgmt(delta_var=DELTA_SMALL), mgmt_yield)] * len(xs)
            st.line_chart({"Elasticity": ys}, x=[int(x * 100) for x in xs])

        else:
            xs = list(range(5_000, 40_001, 5_000))
            ys = [elasticity(mgmt(delta_fix=DELTA_SMALL), mgmt_yield)] * len(xs)
            st.line_chart({"Elasticity": ys}, x=[int(x / 1000) for x in xs])

        st.caption("Elasticity = % change in yield for a 1% change in this input")
        st.divider()

st.caption(
    "Sensitivities and elasticities are local to current assumptions and highlight "
    "where risk concentrates. They are explanatory, not forecasts."
)
