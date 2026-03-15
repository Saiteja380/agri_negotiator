from pydantic import BaseModel, Field

# ==========================================
# 1. INPUT SCHEMA (Frontend -> Backend)
# ==========================================
class NegotiationRequest(BaseModel):
    commodity: str = Field(..., description="The crop being traded, e.g., Potato")
    state: str = Field(..., description="State for Agmarknet data, e.g., Uttar Pradesh")
    quantity_tons: float = Field(..., gt=0, description="Volume in metric tons.")
    start_lat: float = Field(..., description="Origin Latitude")
    start_lon: float = Field(..., description="Origin Longitude")
    end_lat: float = Field(..., description="Destination Latitude")
    end_lon: float = Field(..., description="Destination Longitude")

# ==========================================
# 2. OUTPUT SCHEMA (AI Engine -> Database)
# ==========================================
class NegotiationResult(BaseModel):
    market_baseline_price: float = Field(..., description="The Agmarknet reference price PER TON.")
    farmer_quote_per_ton: float = Field(..., description="Final demanded crop price PER TON by the Farmer.")
    buyer_quote_per_ton: float = Field(..., description="Final offered crop price PER TON by the Buyer.")
    
    transporter_per_km_rate: float = Field(..., description="Freight rate PER KILOMETER calculated by the Transporter.")
    weather_hazard_premium: float = Field(..., description="The extra flat amount added due to bad weather. Output 0.0 if none.")
    transporter_flat_freight: float = Field(..., description="TOTAL flat freight rate for the entire truck journey (NOT per ton).")
    
    final_accepted_price_per_ton: float = Field(..., description="The mathematically agreed CROP price PER TON (excluding transport).")
    agent_reasoning_log: str = Field(..., description="Explainable AI (XAI) log detailing the math and unit breakdown.")