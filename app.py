import streamlit as st
import math

# ---------------- Helper Functions ---------------- #
def convert_discharge(value, unit):
    """Convert discharge to m³/s."""
    if unit == "cusec (ft³/s)":
        return value * 0.0283168
    elif unit == "m³/s":
        return value
    return value

def convert_velocity(value, unit):
    """Convert velocity to m/s."""
    if unit == "ft/s":
        return value * 0.3048
    elif unit == "m/s":
        return value
    return value

def convert_head(value, unit):
    """Convert head to meters."""
    if unit == "meters":
        return value
    elif unit == "feet":
        return value * 0.3048
    return value

def hydraulic_power(rho, g, Q_m3s, H_m):
    """Theoretical hydraulic power (W)."""
    return rho * g * Q_m3s * H_m

def actual_power(P_hydraulic_W, eta_turbine, eta_generator):
    """Actual electrical output power (W)."""
    return P_hydraulic_W * eta_turbine * eta_generator

def penstock_diameter(Q_m3s, v_mps):
    """Penstock diameter (m)."""
    if v_mps <= 0:
        return None
    return math.sqrt((4 * Q_m3s) / (math.pi * v_mps))

def suggest_turbine(H):
    """Suggest turbine type based on net head (m)."""
    if H > 300:
        return "Pelton Turbine (High Head)"
    elif 50 <= H <= 300:
        return "Francis Turbine (Medium Head)"
    else:
        return "Kaplan / Propeller Turbine (Low Head)"

def power_imperial(Q_cusec, H_ft, eta_turbine, eta_generator):
    """Power using weight of water formula (kW)."""
    W = 62.4  # lb/ft³
    return (W * Q_cusec * H_ft * eta_turbine * eta_generator * 746) / (550 * 1000)


# ---------------- Streamlit UI ---------------- #
st.set_page_config(page_title="Mini Hydraulic Power Plant", page_icon="💡", layout="centered")

st.title("💡 Mini Hydraulic Power Plant Calculator")
st.caption("Calculate power, penstock size, and turbine type for your micro hydro project.")

with st.sidebar:
    st.header("📥 User Inputs")

    # Discharge input (3 decimal places)
    Q_value = st.number_input("Discharge Value", value=50.000, min_value=0.000, format="%.3f")
    Q_unit = st.selectbox("Discharge Unit", ["cusec (ft³/s)", "m³/s"])

    # Velocity input (3 decimal places)
    v_value = st.number_input("Velocity Value", value=3.000, min_value=0.000, format="%.3f")
    v_unit = st.selectbox("Velocity Unit", ["ft/s", "m/s"])

    # Head input (3 decimal places)
    H_value = st.number_input("Net Head Value", value=25.000, min_value=0.000, format="%.3f")
    H_unit = st.selectbox("Head Unit", ["meters", "feet"])

    st.markdown("---")
    st.subheader("⚙ Efficiencies")
    eta_turbine = st.number_input("Turbine Efficiency ηₜ (%)", value=85.000, min_value=1.000, max_value=100.000, format="%.3f") / 100
    eta_generator = st.number_input("Generator Efficiency ηg (%)", value=90.000, min_value=1.000, max_value=100.000, format="%.3f") / 100


# ---------------- Conversions ---------------- #
Q_m3s = convert_discharge(Q_value, Q_unit)
v_mps = convert_velocity(v_value, v_unit)
H_m = convert_head(H_value, H_unit)

# Imperial requires Q in cusec and H in feet
Q_cusec = Q_value if Q_unit == "cusec (ft³/s)" else Q_m3s / 0.0283168
H_ft = H_m * 3.281

# ---------------- Calculations ---------------- #
rho, g = 1000, 9.81
P_hydraulic_W = hydraulic_power(rho, g, Q_m3s, H_m)
P_actual_W = actual_power(P_hydraulic_W, eta_turbine, eta_generator)
P_imperial_kW = power_imperial(Q_cusec, H_ft, eta_turbine, eta_generator)

# Penstock Diameter
D_penstock_m = penstock_diameter(Q_m3s, v_mps)
D_penstock_in = D_penstock_m * 39.3701 if D_penstock_m else None

# ---------------- Results ---------------- #
st.subheader("📊 Results")

col1, col2 = st.columns(2)
with col1:
    st.metric("Hydraulic Power (theoretical)", f"{P_hydraulic_W/1000:.3f} kW")
    st.caption("P = ρ g Q H")

with col2:
    st.metric("Electrical Output Power", f"{P_actual_W/1000:.3f} kW")
    st.caption("P_out = P × ηₜ × ηg")

st.markdown("### ⚖ Power (Imperial Formula)")
st.success(f"{P_imperial_kW:.3f} kW (using W·Q·H method)")

st.markdown("### 🚰 Penstock Pipe Diameter")
if D_penstock_m:
    st.success(f"Recommended Diameter ≈ {D_penstock_m:.3f} m  |  {D_penstock_in:.2f} inches (for velocity {v_mps:.3f} m/s)")
else:
    st.error("Invalid velocity selected.")

st.markdown("### ⚙ Suggested Turbine Type")
turbine = suggest_turbine(H_m)
st.info(f"Recommended Turbine: **{turbine}**")
