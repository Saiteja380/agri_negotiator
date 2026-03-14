import streamlit as st
import requests
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# ==========================================
# 0. PAGE CONFIG & AESTHETIC CSS (Motion Graphics)
# ==========================================
st.set_page_config(page_title="Agri-Negotiator AI", layout="wide", page_icon="🌾")

st.markdown("""
    <style>
    /* Sleek gradient background for the header */
    .main-header {
        background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0px;
    }
    
    /* Neon Pulse Animation for the Trigger Button */
    .stButton>button {
        border: 2px solid #38ef7d;
        border-radius: 8px;
        background-color: transparent;
        color: #11998e;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        box-shadow: 0 0 15px #38ef7d;
        transform: translateY(-2px);
        background-color: #38ef7d;
        color: white !important;
    }
    
    /* Smooth slide-up fade-in for the results dashboard */
    .fade-in {
        animation: fadeIn 0.8s ease-out;
    }
    @keyframes fadeIn {
        0% {opacity: 0; transform: translateY(20px);}
        100% {opacity: 1; transform: translateY(0);}
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. THE STATE MACHINE (The Input Freezer)
# ==========================================
# We use session state to track if the engine is currently running
if 'is_negotiating' not in st.session_state:
    st.session_state.is_negotiating = False

def lock_ui():
    """Callback function to freeze all inputs the millisecond the button is clicked."""
    st.session_state.is_negotiating = True

# ==========================================
# HELPER: TEXT TO COORDINATES TRANSLATOR
# ==========================================
@st.cache_data(show_spinner=False)
def get_coordinates(city_name):
    geolocator = Nominatim(user_agent="agri_b2b_negotiator")
    try:
        location = geolocator.geocode(city_name + ", India")
        if location:
            return location.latitude, location.longitude
        return None, None
    except GeocoderTimedOut:
        return None, None

# --- HEADER ---
st.markdown('<div class="main-header">🌾 Agri-Negotiator: B2B AI Trade Engine</div>', unsafe_allow_html=True)
st.markdown("Autonomous multi-agent supply chain negotiation powered by live Agmarknet & OpenWeather data.")

# ==========================================
# 2. THE INPUT PANEL (Left Sidebar)
# ==========================================
with st.sidebar:
    st.header("Trade Parameters")
    
    COMMODITIES = ["Potato", "Tomato", "Onion", "Wheat", "Rice", "Soyabean", "Cotton", "Maize", "Mustard"]
    STATES = ["Andhra Pradesh", "Gujarat", "Haryana", "Karnataka", "Madhya Pradesh", "Maharashtra", "Punjab", "Telangana", "Uttar Pradesh"]
    
    # Notice the 'disabled' parameter is now permanently linked to our state machine
    commodity = st.selectbox("Commodity", COMMODITIES, disabled=st.session_state.is_negotiating)
    state = st.selectbox("Market State", STATES, disabled=st.session_state.is_negotiating)
    quantity_tons = st.number_input("Quantity (Metric Tons)", min_value=0.1, max_value=100.0, value=10.0, step=0.5, disabled=st.session_state.is_negotiating)
    
    st.subheader("Logistics Routing")
    origin_city = st.text_input("Origin City", value="Hyderabad", disabled=st.session_state.is_negotiating)
    dest_city = st.text_input("Destination City", value="Pune", disabled=st.session_state.is_negotiating)

    # The button triggers the lock_ui callback immediately before executing
    trigger_negotiation = st.button("🚀 Trigger AI Negotiation", use_container_width=True, on_click=lock_ui, disabled=st.session_state.is_negotiating)

# ==========================================
# 3. THE DISPLAY PANEL & KINETIC ENGINE
# ==========================================
if st.session_state.is_negotiating:
    
    # KINETIC UI: We replace the boring spinner with an animated Status container
    with st.status("Initializing AI Agents...", expanded=True) as status:
        st.write("📡 Translating city names to satellite coordinates...")
        start_lat, start_lon = get_coordinates(origin_city)
        end_lat, end_lon = get_coordinates(dest_city)
        
        if not start_lat or not end_lat:
            status.update(label="Error in Routing", state="error", expanded=True)
            st.error("🚨 Could not find one of those cities on the map. Please check your spelling.")
            st.session_state.is_negotiating = False
            st.rerun()
            
        st.write("⛈️ Fetching live OpenWeather meteorological data...")
        time.sleep(1) # Tiny pause for aesthetic UI effect
        st.write("📈 Polling Agmarknet government database for baselines...")
        
        payload = {
            "commodity": commodity,
            "state": state,
            "quantity_tons": quantity_tons,
            "start_lat": start_lat,
            "start_lon": start_lon,
            "end_lat": end_lat,
            "end_lon": end_lon
        }
        
        st.write("🤖 AI Agents are now actively negotiating the contract...")
        
        try:
            response = requests.post("http://127.0.0.1:8000/api/v1/negotiate", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                data = result["data"]
                status.update(label="Negotiation Complete!", state="complete", expanded=False)
                
                # FADE IN ANIMATION FOR RESULTS
                st.markdown('<div class="fade-in">', unsafe_allow_html=True)
                
                st.success(f"✅ Contract mathematically sealed! Database Record: **{result['trade_id']}**")
                
                st.subheader("Financial Breakdown (Per Ton)")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Gov Baseline", f"₹{data['market_baseline_price']:,.2f}")
                col2.metric("Farmer Demand", f"₹{data['farmer_quote']:,.2f}")
                col3.metric("Buyer Offer", f"₹{data['buyer_quote']:,.2f}")
                col4.metric("Final Agreed Price", f"₹{data['final_accepted_price']:,.2f}", 
                            delta=f"{data['final_accepted_price'] - data['market_baseline_price']:,.2f} vs Base")
                
                st.subheader("Logistics Breakdown")
                col5, col6 = st.columns(2)
                col5.metric("Rate Per KM", f"₹{data.get('transporter_per_km_rate', 0.0):,.2f}")
                col6.metric("Total Flat Freight", f"₹{data['transporter_quote']:,.2f}")
                
                st.divider()
                
                st.subheader("🧠 Explainable AI (XAI) Log")
                st.info(data['agent_reasoning_log'])
                
                st.subheader("📜 Binding Legal Contract")
                st.text_area("Final Output", data['contract_text'], height=250)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
            elif response.status_code == 429:
                status.update(label="Rate Limit Hit", state="error")
                st.warning("⏳ **Google AI Free Tier Limit Hit!** The API needs to cool down. Wait exactly 60 seconds.")
            else:
                status.update(label="System Error", state="error")
                st.error(f"Backend Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            status.update(label="Connection Failed", state="error")
            st.error("🚨 Could not connect to the Backend Engine! Is your FastAPI server running on port 8000?")
            
    # Unlock the UI after the entire process finishes
    st.session_state.is_negotiating = False
    
    # We create a manual reset button to clear the screen for the next trade
    if st.button("Start New Negotiation"):
        st.rerun()