import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ORS_API_KEY = os.getenv("ROUTING_API_KEY")
GOV_DATA_API_KEY = os.getenv("GOV_DATA_API_KEY")

# ==========================================
# IN-MEMORY CACHE FOR BACKGROUND WORKER
# ==========================================
agmarket_cache = {
    "states": ["Telangana", "Maharashtra", "Uttar Pradesh", "Punjab", "Karnataka"],
    "commodities": ["Rice", "Tomato", "Potato", "Wheat", "Onion"],
    "last_updated": None
}

def update_agmarket_cache():
    """Background worker function: Fetches massive data and updates the RAM cache."""
    print("🔄 [BACKGROUND TASK] Fetching fresh AgMarket lists...")
    resource_id = "9ef84268-d588-465a-a308-a864a43d0070" 
    url = f"https://api.data.gov.in/resource/{resource_id}?api-key={GOV_DATA_API_KEY}&format=json&limit=10000"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if "records" in data and data["records"]:
            df = pd.DataFrame(data["records"])
            
            # Update the global cache dictionary
            agmarket_cache["states"] = sorted(df['state'].dropna().unique().tolist())
            agmarket_cache["commodities"] = sorted(df['commodity'].dropna().unique().tolist())
            agmarket_cache["last_updated"] = datetime.now()
            print(f"✅ [BACKGROUND TASK] Cache updated successfully at {agmarket_cache['last_updated']}")
            
    except Exception as e:
        print(f"⚠️ [BACKGROUND TASK] Failed to update cache. Using existing data. Error: {e}")

def get_dynamic_agmarket_lists():
    """Instant retrieval from the RAM cache for the UI."""
    return agmarket_cache["states"], agmarket_cache["commodities"]

def get_weather_forecast(lat: float, lon: float) -> str:
    """Fetches a free 5-day weather forecast from Open-Meteo."""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=precipitation_sum&timezone=auto"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        total_rain = sum(data.get('daily', {}).get('precipitation_sum', [0]))
        
        if total_rain > 10.0:
            return "Heavy rain expected. High risk of crop spoilage."
        elif total_rain > 0:
            return "Light rain expected."
        return "Clear weather expected."
    except Exception as e:
        print(f"Weather API failed: {e}")
        return "Weather forecast currently unavailable."

def get_driving_distance(start_lon: float, start_lat: float, end_lon: float, end_lat: float) -> float:
    """Calculates exact driving distance using OpenRouteService."""
    url = f"https://api.openrouteservice.org/v2/directions/driving-car?api_key={ORS_API_KEY}&start={start_lon},{start_lat}&end={end_lon},{end_lat}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        distance_km = data['features'][0]['properties']['segments'][0]['distance'] / 1000
        return round(distance_km, 2)
    except Exception as e:
        print(f"Routing API failed: {e}")
        return 300.0 

def get_mandi_price(state: str, commodity: str) -> float:
    """Fetches official government APMC mandi prices and sorts them safely in Python."""
    url = f"https://api.data.gov.in/resource/35985678-0d79-46b4-9ed6-6f13308a1d24?api-key={GOV_DATA_API_KEY}&format=json&filters[state]={state}&filters[commodity]={commodity}&limit=100"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        records = data.get('records', [])
        if len(records) > 0:
            records.sort(key=lambda x: datetime.strptime(x.get('Arrival_Date', '01/01/2000'), "%d/%m/%Y"), reverse=True)
            return float(records[0]['Modal_Price'])
        else:
            raise ValueError(f"No records found for {commodity} in {state}.")
            
    except Exception as e:
        print(f"Agmarknet API unavailable. Activating fallback local data for {commodity}...")
        fallbacks = {
            "Wheat": 2250.0,
            "Rice": 3100.0,
            "Soybean": 4500.0,
            "Tomato": 700.0 
        }
        return fallbacks.get(commodity, 2000.0)