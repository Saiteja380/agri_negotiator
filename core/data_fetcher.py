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
    "states": ["Telangana", "Maharashtra", "Uttar Pradesh", "Punjab", "Karnataka"], # Fallbacks
    "commodities": ["Rice", "Tomato", "Potato", "Wheat", "Onion"], # Fallbacks
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

# ... (Keep your existing get_weather_forecast, get_driving_distance, and get_mandi_price functions below this exactly as they are) ...