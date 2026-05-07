import streamlit as st
import requests
import pandas as pd
from geopy.geocoders import Nominatim
import time

# ==========================================
# 1. PAGE CONFIGURATION & CLEAN AESTHETICS
# ==========================================
st.set_page_config(
    page_title="Agri-Negotiator Pro V2",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    /* Force White Labels for all input fields */
    label, .st-emotion-cache-10trnc2, [data-testid="stSidebar"] label {
        color: #ffffff !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
    }

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
    
    /* Custom Footer Styling */
    .footer-tag {
        text-align: center;
        padding-top: 20px;
        color: #888;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATA HELPERS
# ==========================================
def get_coordinates(city_name):
    if not city_name:
        return (0.0, 0.0)
    try:
        geolocator = Nominatim(user_agent="agri_pro_v2")
        location = geolocator.geocode(f"{city_name}, India")
        return (location.latitude, location.longitude) if location else (0.0, 0.0)
    except: 
        return (0.0, 0.0)

@st.cache_data(ttl=3600)
def load_dropdown_options():
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1/reference-data", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("states") and data.get("commodities"):
                return data["states"], data["commodities"]
    except:
        pass
    return ["Telangana", "Maharashtra", "Uttar Pradesh", "Karnataka"], ["Tomato", "Potato", "Rice", "Wheat", "Onion"]

available_states, available_commodities = load_dropdown_options()

# ==========================================
# 3. SIDEBAR PARAMETERS (BLANK BY DEFAULT)
# ==========================================
st.sidebar.title("🌾 Trade Control")
st.sidebar.markdown("---")

commodity = st.sidebar.selectbox("Commodity", available_commodities)
state = st.sidebar.selectbox("State", available_states)

# Fields are now blank by default using value="" and placeholders
origin_city = st.sidebar.text_input("Origin", value="", placeholder="Enter origin city...")
destination_city = st.sidebar.text_input("Destination", value="", placeholder="Enter destination city...")
volume = st.sidebar.number_input("Volume (Tons)", value=0.0, step=0.5)

st.sidebar.markdown("<br>", unsafe_allow_html=True)
negotiate_btn = st.sidebar.button("🚀 INITIATE SMART CONTRACT", type="primary", use_container_width=True)

st.sidebar.markdown("---")
# THE DEMO SAVER: Pitch Mode Toggle
pitch_mode = st.sidebar.checkbox("⚡ Pitch Mode (Instant Demo)", value=True, help="Bypasses live LLM for instant investor presentations.")

# ==========================================
# 4. DASHBOARD RENDER FUNCTION
# ==========================================
def render_dashboard_layout(data, map_data, is_active=False):
    """Renders the static skeleton layout of the dashboard to prevent UI shifting."""
    st.markdown("### Market Discovery Analytics")
    col_map, col_metrics = st.columns([1, 1.5])
    
    with col_map:
        # Prevent the map from breaking if coordinates are empty
        if map_data.iloc[0]['lat'] == 0.0 and map_data.iloc[0]['lon'] == 0.0:
            st.info("🗺️ Awaiting location data to render route map.")
        else:
            st.map(map_data, zoom=5, height=280)
    
    with col_metrics:
        m1, m2 = st.columns(2)
        m1.markdown(f'<div class="metric-card"><div class="metric-title">🏛️ Gov Baseline</div><div class="metric-value">₹{data.get("agmarknet_baseline", 0):,.2f}</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-card"><div class="metric-title">👨‍🌾 Farmer Ask</div><div class="metric-value">₹{data.get("farmer_quote", 0):,.2f}</div></div>', unsafe_allow_html=True)
        
        m3, m4 = st.columns(2)
        m3.markdown(f'<div class="metric-card"><div class="metric-title">💼 Buyer Offer</div><div class="metric-value">₹{data.get("buyer_quote", 0):,.2f}</div></div>', unsafe_allow_html=True)
        border_color = "#28a745" if is_active else "#e0e0e0"
        m4.markdown(f'<div class="metric-card" style="border-bottom: 4px solid {border_color};"><div class="metric-title">⚖️ Final Accepted / Ton</div><div class="metric-value">₹{data.get("final_accepted_price_per_ton", 0):,.2f}</div></div>', unsafe_allow_html=True)

    st.divider()

    st.markdown("### Logistical Breakdown")
    l1, l2, l3, l4 = st.columns(4)
    l1.metric("Route Distance 📍", f"{data.get('total_distance_km', 0):,.0f} km")
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
            Please enter parameters in the Trade Control sidebar and click 'Initiate Smart Contract' to deploy the autonomous agents.
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 5. MAIN EXECUTION FLOW
# ==========================================
st.markdown("## Agri-Supply Multi-Agent Negotiator")
st.caption("Enterprise B2B Settlement Engine | Verified via Deterministic Math")

s_lat, s_lon = get_coordinates(origin_city)
e_lat, e_lon = get_coordinates(destination_city)
map_data_df = pd.DataFrame({'lat': [s_lat, e_lat], 'lon': [s_lon, e_lon]})

# --- IDLE STATE ---
if not negotiate_btn:
    render_dashboard_layout({}, map_data_df, is_active=False)

# --- ACTIVE NEGOTIATION STATE ---
if negotiate_btn:
    # Safety Check: Prevent execution if fields are left totally blank
    if not origin_city or not destination_city or volume <= 0:
        st.error("🚨 Please enter an Origin, Destination, and a Volume greater than 0.")
        render_dashboard_layout({}, map_data_df, is_active=False)
    else:
        payload = {"commodity": commodity, "state": state, "quantity_tons": volume,
                   "start_lat": s_lat, "start_lon": s_lon, "end_lat": e_lat, "end_lon": e_lon}
        
        with st.status("🤖 Initiating Swarm Intelligence...", expanded=True) as status:
            st.write("👨‍🌾 Farmer Agent analyzing local Agmarknet baselines...")
            time.sleep(0.8)
            st.write("🚚 Transporter Agent calculating route distance and hazard premiums...")
            time.sleep(0.8)
            st.write("💼 Buyer Agent generating aggressive counter-offer...")
            time.sleep(0.8)
            st.write("⚖️ Arbitrator Agent enforcing median mathematical settlement...")
            
            try:
                if pitch_mode:
                    # STAGED DEMO DATA FOR PRESENTATION (Dynamically injects your inputs)
                    time.sleep(1) # Final dramatic pause
                    
                    true_landed_cost = (volume * 25800.0) + 6987.50
                    
                    live_data = {
                        "agmarknet_baseline": 25000.0,
                        "farmer_quote": 26500.0,
                        "buyer_quote": 25100.0,
                        "final_accepted_price_per_ton": 25800.0,
                        "total_distance_km": 215,
                        "rate_per_km": 32.50,
                        "weather_premium": 0.0,
                        "transporter_flat_freight": 6987.50,
                        "true_landed_cost": true_landed_cost,
                        "agent_reasoning_log": "The Farmer demanded ₹26,500 citing labor costs, while the Buyer capped at ₹25,100 based on retail forecasts. I enforced the median mathematical settlement of ₹25,800 to guarantee margins for both parties.",
                        "contract_text": f"LEGAL AGREEMENT [May 07, 2026]: The parties mutually agree to the trade execution of {volume} metric tons of {commodity}. The route from {origin_city.title()} to {destination_city.title()} covers an estimated driving distance of 215 km. The finalized farm-gate price is ₹25,800.00 per ton. An additional flat logistics freight fee of ₹6,987.50 has been authorized. The Final True Landed Cost payable by the Buyer is strictly locked at ₹{true_landed_cost:,.2f}."
                    }
                    response_status = 200
                else:
                    # LIVE BACKEND CONNECTION
                    response = requests.post("http://127.0.0.1:8000/api/v1/negotiate", json=payload)
                    response_status = response.status_code
                    live_data = response.json().get("data", {}) if response_status == 200 else {}
                
                if response_status == 200:
                    status.update(label="✅ Smart Contract Finalized!", state="complete", expanded=False)
                    render_dashboard_layout(live_data, map_data_df, is_active=True)

                elif response_status == 429:
                    status.update(label="🚨 Quota Exhausted", state="error", expanded=True)
                    st.error("API Limit Reached. Please wait 60 seconds.")
                    render_dashboard_layout({}, map_data_df, is_active=False)
                else:
                    status.update(label="🚨 System Error", state="error", expanded=True)
                    st.error("Backend Failed to process request.")
                    render_dashboard_layout({}, map_data_df, is_active=False)

            except requests.exceptions.ConnectionError:
                status.update(label="🚨 Connection Severed", state="error", expanded=True)
                st.error("Could not connect to the backend server.")
                render_dashboard_layout({}, map_data_df, is_active=False)

# ==========================================
# 6. FOOTER BRANDING
# ==========================================
st.markdown("---")
st.markdown('<div class="footer-tag">⚙️ Engineered by Saiteja | Powered by Google Gemini Multi-Agent AI</div>', unsafe_allow_html=True)