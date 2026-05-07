import streamlit as st
import requests
import pandas as pd
from geopy.geocoders import Nominatim

# ==========================================
# 1. PAGE CONFIGURATION & CLEAN AESTHETICS
# ==========================================
st.set_page_config(
    page_title="Agri-Negotiator Pro V2",
    page_icon="🌾",
    layout="wide"
)

st.markdown("""
    <style>
    /* Clean, light metric cards */
    .metric-card {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 15px;
        border: 1px solid #e0e0e0;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.02);
        text-align: center;
        margin-bottom: 15px;
    }
    .metric-title { font-size: 0.85rem; color: #666; font-weight: 600; text-transform: uppercase; margin-bottom: 5px; }
    .metric-value { font-size: 1.6rem; font-weight: 700; color: #111; margin: 0; }
    
    /* Clean contract box */
    .contract-box {
        background: #f8f9fa;
        border-left: 4px solid #28a745;
        padding: 20px;
        border-radius: 4px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.9rem;
        color: #333;
        line-height: 1.5;
    }
    
    /* Inactive contract box for idle state */
    .contract-box-idle {
        background: #f8f9fa;
        border-left: 4px solid #cccccc;
        padding: 20px;
        border-radius: 4px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.9rem;
        color: #888;
        line-height: 1.5;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATA HELPERS
# ==========================================
def get_coordinates(city_name):
    try:
        geolocator = Nominatim(user_agent="agri_pro_v2")
        location = geolocator.geocode(f"{city_name}, India")
        return (location.latitude, location.longitude) if location else (0.0, 0.0)
    except: 
        return (0.0, 0.0)

@st.cache_data(ttl=3600)
def load_dropdown_options():
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1/reference-data", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("states") and data.get("commodities"):
                return data["states"], data["commodities"]
    except:
        pass
    return ["Telangana", "Maharashtra", "Uttar Pradesh", "Karnataka"], ["Tomato", "Potato", "Rice", "Wheat", "Onion"]

available_states, available_commodities = load_dropdown_options()

# ==========================================
# 3. SIDEBAR PARAMETERS
# ==========================================
st.sidebar.title("🌾 Trade Control")
st.sidebar.markdown("---")

commodity = st.sidebar.selectbox("Commodity", available_commodities)
state = st.sidebar.selectbox("State", available_states)
origin_city = st.sidebar.text_input("Origin", "Karimnagar")
destination_city = st.sidebar.text_input("Destination", "Nalgonda")
volume = st.sidebar.number_input("Volume (Tons)", value=2.37)

st.sidebar.markdown("<br>", unsafe_allow_html=True)
negotiate_btn = st.sidebar.button("🚀 INITIATE SMART CONTRACT", type="primary", use_container_width=True)

# ==========================================
# 4. DASHBOARD RENDER FUNCTION
# ==========================================
def render_dashboard_layout(data, map_data, is_active=False):
    """Renders the static skeleton layout of the dashboard to prevent UI shifting."""
    
    st.markdown("### Market Discovery Analytics")
    col_map, col_metrics = st.columns([1, 1.5])
    
    with col_map:
        st.map(map_data, zoom=5, height=280)
    
    with col_metrics:
        m1, m2 = st.columns(2)
        m1.markdown(f'<div class="metric-card"><div class="metric-title">🏛️ Gov Baseline</div><div class="metric-value">₹{data.get("agmarknet_baseline", 0):,.2f}</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-card"><div class="metric-title">👨‍🌾 Farmer Ask</div><div class="metric-value">₹{data.get("farmer_quote", 0):,.2f}</div></div>', unsafe_allow_html=True)
        
        m3, m4 = st.columns(2)
        m3.markdown(f'<div class="metric-card"><div class="metric-title">💼 Buyer Offer</div><div class="metric-value">₹{data.get("buyer_quote", 0):,.2f}</div></div>', unsafe_allow_html=True)
        
        # Highlight the final price if active, keep it grey if idle
        border_color = "#28a745" if is_active else "#e0e0e0"
        m4.markdown(f'<div class="metric-card" style="border-bottom: 4px solid {border_color};"><div class="metric-title">⚖️ Final Accepted / Ton</div><div class="metric-value">₹{data.get("final_accepted_price_per_ton", 0):,.2f}</div></div>', unsafe_allow_html=True)

    st.divider()

    st.markdown("### Logistical Breakdown")
    l1, l2, l3, l4 = st.columns(4)
    l1.metric("Distance 📍", f"{data.get('total_distance_km', 0):,.0f} km")
    l2.metric("Base Rate ⛽", f"₹{data.get('rate_per_km', 0):,.2f}/km")
    l3.metric("Hazards ⛈️", f"₹{data.get('weather_premium', 0):,.2f}")
    l4.metric("Total Freight 📦", f"₹{data.get('transporter_flat_freight', 0):,.2f}")

    st.markdown("### 📜 Digital B2B Contract")
    
    if is_active:
        st.success(f"**Final True Landed Cost: ₹{data.get('true_landed_cost', 0):,.2f}**")
        st.markdown(f"""
        <div class="contract-box">
            <strong>[Arbitrator Log]</strong><br>
            {data.get('agent_reasoning_log', 'N/A')}<br><br>
            <strong>[Legal Execution]</strong><br>
            {data.get('contract_text', 'N/A')}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("**Awaiting Trade Initiation...**")
        st.markdown("""
        <div class="contract-box-idle">
            <strong>[System Idle]</strong><br>
            Please verify the parameters in the Trade Control sidebar and click 'Initiate Smart Contract' to deploy the autonomous agents.
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 5. MAIN EXECUTION FLOW
# ==========================================
st.markdown("## Agri-Supply Multi-Agent Negotiator")
st.caption("Enterprise B2B Settlement Engine | Verified via Deterministic Math")

# Pre-calculate coordinates for the map
s_lat, s_lon = get_coordinates(origin_city)
e_lat, e_lon = get_coordinates(destination_city)
map_data_df = pd.DataFrame({'lat': [s_lat, e_lat], 'lon': [s_lon, e_lon]})

# --- IDLE STATE ---
if not negotiate_btn:
    # Pass empty data to keep the structure intact
    empty_data = {}
    render_dashboard_layout(empty_data, map_data_df, is_active=False)

# --- ACTIVE NEGOTIATION STATE ---
if negotiate_btn:
    payload = {"commodity": commodity, "state": state, "quantity_tons": volume,
               "start_lat": s_lat, "start_lon": s_lon, "end_lat": e_lat, "end_lon": e_lon}
    
    with st.status("🤖 Initiating Swarm Intelligence...", expanded=True) as status:
        st.write("👨‍🌾 Farmer Agent analyzing local Agmarknet baselines...")
        st.write("🚚 Transporter Agent calculating route distance and hazard premiums...")
        
        try:
            response = requests.post("http://127.0.0.1:8000/api/v1/negotiate", json=payload)
            
            st.write("💼 Buyer Agent generating aggressive counter-offer...")
            st.write("⚖️ Arbitrator Agent enforcing median mathematical settlement...")
            
            if response.status_code == 200:
                status.update(label="✅ Smart Contract Finalized!", state="complete", expanded=False)
                live_data = response.json().get("data", {})
                
                # Render the exact same layout, but with the live data
                render_dashboard_layout(live_data, map_data_df, is_active=True)

            elif response.status_code == 429:
                status.update(label="🚨 Quota Exhausted", state="error", expanded=True)
                st.error("API Limit Reached. Please wait 60 seconds.")
                render_dashboard_layout({}, map_data_df, is_active=False)
            else:
                status.update(label="🚨 System Error", state="error", expanded=True)
                st.error(f"Backend Error: {response.text}")
                render_dashboard_layout({}, map_data_df, is_active=False)

        except requests.exceptions.ConnectionError:
            status.update(label="🚨 Connection Severed", state="error", expanded=True)
            st.error("Could not connect to the backend server.")
            render_dashboard_layout({}, map_data_df, is_active=False)