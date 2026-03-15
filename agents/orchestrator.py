import json
import time
import os
from datetime import datetime
from crewai import Task, Crew, Process
from agents.personas import AgriAgents
from core.data_fetcher import get_weather_forecast, get_driving_distance, get_mandi_price
from api.schemas import NegotiationResult

# ==========================================
# THE PHYSICAL GOVERNOR (API FREE TIER PROTECTION)
# ==========================================
def api_throttle(agent_output):
    """
    Physically freezes the Python thread for 15 seconds after every single LLM thought.
    This guarantees we stay safely under the Google Free Tier rate limits.
    """
    print(f"\n⏳ [PHYSICAL BRAKE] Agent thought complete. Cooling down API for 15 seconds...")
    time.sleep(15)

def run_negotiation(commodity: str, state: str, start_lat: float, start_lon: float, end_lat: float, end_lon: float, quantity_tons: float):
    print(f"\n[SYSTEM] Fetching Live Market & Logistics Data for {commodity}...")
    
    # 1. Fetch live parameters
    weather = get_weather_forecast(start_lat, start_lon)
    distance = get_driving_distance(start_lon, start_lat, end_lon, end_lat)
    mandi_price_quintal = get_mandi_price(state, commodity)
    mandi_price_ton = mandi_price_quintal * 10
    
    # Generate a dynamic timestamp for the contract execution
    current_date = datetime.now().strftime("%A, %B %d, %Y")
    
    print(f"[SYSTEM] Data Secured! Weather: {weather} | Route: {distance}km | Gov Baseline: ₹{mandi_price_ton}/ton\n")

    # 2. Initialize Agents
    agents = AgriAgents()
    farmer = agents.farmer_agent(baseline_price=mandi_price_ton)
    buyer = agents.buyer_agent(commodity=commodity, quantity=quantity_tons, weather=weather)
    transporter = agents.transporter_agent(distance=distance, weather=weather)
    arbitrator = agents.arbitrator_agent()

    # ==========================================
    # 3. DEFINE TASKS (GRANULAR DASHBOARD UPGRADE)
    # ==========================================
    farmer_task = Task(
        description=f"Propose your initial selling price for {quantity_tons} tons of {commodity}. Base market price is ₹{mandi_price_ton}/ton. Justify your price based on labor. MUST quote PER TON.",
        expected_output="A clear initial price offer PER TON from the Farmer.",
        agent=farmer
    )

    transporter_task = Task(
        description=f"Provide your freight quote for the {distance}km journey for a {quantity_tons} ton truckload. Factor in the current weather: '{weather}'. MUST quote the rate PER KM, any extra WEATHER HAZARD premium, and the TOTAL flat fee.",
        expected_output="Rate PER KM, weather premium amount, and a TOTAL flat freight rate.",
        agent=transporter
    )

    buyer_task = Task(
        description=f"Review the Farmer's crop price (Per Ton) and the Transporter's freight quote. Negotiate aggressively. Provide your counter-offer PER TON for the crop.",
        expected_output="A strict counter-offer to both the Farmer and Transporter.",
        agent=buyer
    )

    finalize_task = Task(
        description=(
            f"Review the quotes. Mediate a final compromise.\n"
            "CRITICAL UNIT RULES:\n"
            "1. 'farmer_quote_per_ton' and 'buyer_quote_per_ton' MUST be expressed as PER TON prices.\n"
            "2. 'transporter_per_km_rate' MUST be the final agreed rate PER KILOMETER.\n"
            "3. 'weather_hazard_premium' MUST be the extra amount added due to weather. If none, output 0.0.\n"
            "4. 'transporter_flat_freight' MUST be expressed as the TOTAL flat fee for the whole trip.\n"
            "5. 'final_accepted_price_per_ton' MUST be the agreed CROP price PER TON, do not add freight to this specific number.\n"
            "6. 'agent_reasoning_log' must explain the spread between the Farmer and Buyer per-ton quotes before the final median was chosen (maximum 3 sentences).\n"
            "7. STRICT RULE: Output ONLY raw JSON data matching the NegotiationResult schema. Do NOT use markdown code blocks."
        ),
        expected_output="Strict JSON object with all dashboard metrics.",
        agent=arbitrator,
        output_json=NegotiationResult 
    )

    # ==========================================
    # 4. ASSEMBLE CREW (V1 STABLE CONFIG)
    # ==========================================
    negotiation_crew = Crew(
        agents=[farmer, transporter, buyer, arbitrator],
        tasks=[farmer_task, transporter_task, buyer_task, finalize_task],
        process=Process.sequential, 
        max_rpm=1,  
        step_callback=api_throttle, 
        verbose=True,
        memory=False  # 🟢 THE SHIELD: Disables OpenAI memory dependencies
    )

    print("--- Initiating AI Agent Negotiation Sequence ---")
    result = negotiation_crew.kickoff()

    # ==========================================
    # 5. THE MARKDOWN SCRUBBER & EXTRACTION
    # ==========================================
    ai_data = {}
    
    if hasattr(result, 'pydantic') and result.pydantic:
        ai_data = result.pydantic.model_dump()
    elif hasattr(result, 'json_dict') and result.json_dict:
        ai_data = result.json_dict
    else:
        raw_text = result.raw.strip()
        
        # Safely strip markdown block indicators
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:]
            
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
            
        try:
            ai_data = json.loads(raw_text.strip())
        except Exception as e:
            print(f"\n[PARSING ERROR] Failed to clean JSON: {e}")
            ai_data = {}

    # 🛑 THE SAFETY NET: Prevents 'NoneType' crashes if AI fails
    ai_data = ai_data or {}

    # ==========================================
    # 6. THE DETERMINISTIC MATH OVERRIDE (DASHBOARD EDITION)
    # ==========================================
    # Extract ALL dashboard variables safely
    final_price_per_ton = float(ai_data.get("final_accepted_price_per_ton", 0.0))
    flat_freight = float(ai_data.get("transporter_flat_freight", 0.0))
    farmer_quote = float(ai_data.get("farmer_quote_per_ton", 0.0))
    buyer_quote = float(ai_data.get("buyer_quote_per_ton", 0.0))
    rate_per_km = float(ai_data.get("transporter_per_km_rate", 0.0))
    weather_premium = float(ai_data.get("weather_hazard_premium", 0.0))
    
    # Final calculations performed strictly in Python
    total_crop_value = final_price_per_ton * float(quantity_tons)
    true_landed_cost = total_crop_value + flat_freight
    
    # Build the verified legal agreement
    deterministic_contract = (
        f"LEGAL AGREEMENT [{current_date}]:\n"
        f"The parties mutually agree to the trade execution of {quantity_tons} metric tons of {commodity}. "
        f"The route covers a total driving distance of {distance} km. "
        f"The finalized farm-gate price is ₹{final_price_per_ton:,.2f} per ton, yielding a Total Crop Value of ₹{total_crop_value:,.2f}. "
        f"An additional flat logistics freight fee of ₹{flat_freight:,.2f} has been authorized. "
        f"The Final True Landed Cost payable by the Buyer is strictly locked at ₹{true_landed_cost:,.2f}."
    )
    
    # Bundle EVERYTHING for the Streamlit UI (including total distance)
    ai_data.update({
        "total_distance_km": float(distance),
        "agmarknet_baseline": float(mandi_price_ton),
        "farmer_quote": farmer_quote,
        "buyer_quote": buyer_quote,
        "rate_per_km": rate_per_km,
        "weather_premium": weather_premium,
        "total_crop_value": total_crop_value,
        "true_landed_cost": true_landed_cost,
        "contract_text": deterministic_contract,
        "math_verified": True
    })
    
    print(f"\n✅ Math Verified. Landed Cost: ₹{true_landed_cost:,.2f}")
    return ai_data