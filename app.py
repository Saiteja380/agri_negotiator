import streamlit as st
import requests
import pydeck as pdk
from geopy.geocoders import Nominatim
import pandas as pd
import time
from streamlit_lottie import st_lottie

# ==========================================
# 1. PAGE CONFIGURATION & AESTHETICS
# ==========================================
st.set_page_config(
    page_title="Agri-Negotiator Pro V2",
    page_icon="🌾",
    layout="wide"
)

# Custom CSS for glassmorphism and animated borders
st.markdown("""
    <style>
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
        transition: transform 0.3s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        border: 1px solid #00ff80;
    }
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #00ff80 , #0072ff);
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. ASSETS & HELPERS
# ==========================================
def load_lottie(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except:
        return None

lottie_ai = load_lottie("https://assets10.lottiefiles.com/packages/lf20_m6cu96.json")

def get_coordinates(city_name):
    try:
        geolocator = Nominatim(user_agent="agri_pro_v2")
        location = geolocator.geocode(f"{city_name}, India")
        return (location.latitude, location.longitude) if location else (0.0, 0.0)
    except: 
        return (0.0, 0.0)

# ==========================================
# 3. SIDEBAR PARAMETERS
# ==========================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2329/2329094.png", width=100)
st.sidebar.title("Trade Control")

commodity = st.sidebar.selectbox("Commodity", ["Rice", "Tomato", "Potato", "Wheat", "Onion"])
state = st.sidebar.selectbox("State", ["Telangana", "Maharashtra", "Uttar Pradesh", "Punjab", "Karnataka"])
origin_city = st.sidebar.text_input("Origin", "Karimnagar")
destination_city = st.sidebar.text_input("Destination", "Nalgonda")
volume = st.sidebar.number_input("Volume (Tons)", value=2.37)

negotiate_btn = st.sidebar.button("🚀 INITIATE SMART CONTRACT", type="primary", use_container_width=True)

# ==========================================
# 4. MAIN DASHBOARD LAYOUT
# ==========================================
st.title("🌾 Agri-Supply Multi-Agent Negotiator")
st.caption("Enterprise B2B Settlement Engine | Verified via Deterministic Math")

# Top Layout: Smaller Map and Process Flow
top_col1, top_col2 = st.columns([1, 1])

with top_col1:
    st.markdown("### 🗺️ Logistics Route")
    map_placeholder = st.empty()
    
    # Initial Map State
    s_lat, s_lon = get_coordinates(origin_city)
    e_lat, e_lon = get_coordinates(destination_city)
    
    view_state = pdk.ViewState(latitude=(s_lat+e_lat)/2, longitude=(s_lon+e_lon)/2, zoom=6, pitch=45)
    
    if s_lat and e_lat:
        arc_layer = pdk.Layer("ArcLayer", data=[{"s": [s_lon, s_lat], "t": [e_lon, e_lat]}], 
                              get_source_position="s", get_target_position="t", 
                              get_source_color=[0, 255, 128], get_target_color=[255, 114, 0], get_width=5)
        map_placeholder.pydeck_chart(pdk.Deck(layers=[arc_layer], initial_view_state=view_state))

with top_col2:
    st.markdown("### ⚙️ Live Negotiation Flow")
    progress_bar = st.progress(0)
    status_text = st.empty()
    flow_placeholder = st.empty()

# ==========================================
# 5. EXECUTION LOGIC
# ==========================================
if negotiate_btn:
    # STEP 1: Data Ingestion
    status_text.markdown("🟡 **Step 1:** Ingesting Agmarknet & Weather Data...")
    progress_bar.progress(25)
    flow_placeholder.info("🕵️ Farmer Agent: Checking current mandi rates in " + state)
    
    payload = {"commodity": commodity, "state": state, "quantity_tons": volume,
               "start_lat": s_lat, "start_lon": s_lon, "end_lat": e_lat, "end_lon": e_lon}
    
    try:
        response = requests.post("http://127.0.0.1:8000/api/v1/negotiate", json=payload)
        
        # STEP 2 & 3: Agent Turns (Visual Simulation)
        time.sleep(1) 
        status_text.markdown("🟠 **Step 2:** Multi-Agent Price Discovery...")
        progress_bar.progress(50)
        flow_placeholder.warning("🚚 Transporter Agent: Calculating hazard premium for current weather...")
        
        time.sleep(1)
        status_text.markdown("🔵 **Step 3:** Finalizing Arbitrated Settlement...")
        progress_bar.progress(75)
        flow_placeholder.success("⚖️ Arbitrator Agent: Enforcing median compromise on deadlock...")

        # --- RESPONSE HANDLING ---
        if response.status_code == 200:
            raw_data = response.json()
            data = raw_data.get("data", raw_data) # Smart Unwrapper
            
            progress_bar.progress(100)
            status_text.markdown("🟢 **Contract Finalized!**")
            
            st.divider()

            # --- AESTHETIC METRIC SECTION ---
            st.markdown("### 📊 Market Discovery Analytics")
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            
            with m_col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.write("🏛️ Gov Baseline")
                st.subheader(f"₹{data.get('agmarknet_baseline', 0):,.2f}")
                st.markdown('</div>', unsafe_allow_html=True)

            with m_col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.write("👨‍🌾 Farmer Ask")
                st.subheader(f"₹{data.get('farmer_quote', 0):,.2f}")
                st.markdown('</div>', unsafe_allow_html=True)

            with m_col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.write("💼 Buyer Offer")
                st.subheader(f"₹{data.get('buyer_quote', 0):,.2f}")
                st.markdown('</div>', unsafe_allow_html=True)

            with m_col4:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.write("⚖️ Final Price")
                st.subheader(f"₹{data.get('final_accepted_price_per_ton', 0):,.2f}")
                st.caption("Mathematically Resolved")
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("### 🚛 Logistical Breakdown")
            l_col1, l_col2, l_col3, l_col4 = st.columns(4)
            l_col1.metric("Distance", f"{data.get('total_distance_km', 0):,.2f} km", "📍")
            l_col2.metric("Base Rate", f"₹{data.get('rate_per_km', 0):,.2f}/km", "⛽")
            l_col3.metric("Weather Premium", f"₹{data.get('weather_premium', 0):,.2f}", "⛈️")
            l_col4.metric("Total Freight", f"₹{data.get('transporter_flat_freight', 0):,.2f}", "📦")

            st.divider()

            # --- FINAL SETTLEMENT ---
            f_col1, f_col2 = st.columns([1, 2])
            with f_col1:
                if lottie_ai: st_lottie(lottie_ai, height=200)
            with f_col2:
                st.markdown("### 📜 Digital B2B Contract")
                st.success(f"**Final True Landed Cost: ₹{data.get('true_landed_cost', 0):,.2f}**")
                st.info(f"**Arbitrator Log:** {data.get('agent_reasoning_log')}")
                st.code(data.get('contract_text'), language="text")

        # 🛡️ THE RATE LIMIT INTERCEPTOR (429 Error)
        elif response.status_code == 429:
            progress_bar.empty()
            flow_placeholder.empty()
            status_text.error("🚫 API Quota Exhausted")
            st.warning("The Gemini Free Tier allows 15 requests per minute. Please wait for the cooldown.")
            
            # Simple UI text placeholder instead of full sleep lock
            st.info("⏱️ Cooldown active. Please wait 60 seconds before initiating a new trade.")

        else:
            progress_bar.empty()
            status_text.error("❌ System Error")
            st.error(f"Backend Error [{response.status_code}]: {response.text}")

    except requests.exceptions.ConnectionError:
        st.error("🚨 Critical Error: Could not connect to the backend. Is your Uvicorn server running?")

# Footer for Portfolio Credit
st.markdown("---")
st.caption("Engineered by Sai Teja | Built on Gemini 2.5 Flash & CrewAI")