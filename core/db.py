import os
import uuid
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(url, key)

def save_contract_to_db(commodity: str, quantity_tons: float, result_data: dict):
    try:
        trade_id = f"TRD-{str(uuid.uuid4())[:8].upper()}"
        
        response = supabase.table('b2b_contracts').insert({
            "trade_id": trade_id,
            "commodity": commodity,
            "quantity_tons": quantity_tons,
            "market_baseline_price": result_data.get("market_baseline_price", 0.0),
            "farmer_quote": result_data.get("farmer_quote", 0.0),
            "buyer_quote": result_data.get("buyer_quote", 0.0),
            
            # NEW: Pushing the per-km rate to your database
            "transporter_per_km_rate": result_data.get("transporter_per_km_rate", 0.0),
            "transporter_quote": result_data.get("transporter_quote", 0.0),
            
            "final_accepted_price": result_data.get("final_accepted_price", 0.0),
            "contract_text": result_data.get("contract_text", "Error generating text"),
            "agent_reasoning_log": result_data.get("agent_reasoning_log", "N/A"),
            "status": "Pending"
        }).execute()
        
        print(f"\n[DATABASE] Success! Contract {trade_id} saved to Supabase.")
        return trade_id
        
    except Exception as e:
        print(f"\n[DATABASE ERROR] Failed to save to Supabase: {e}")
        return None