from crewai import Task, Crew, Process
from agents.personas import AgriAgents
from core.data_fetcher import get_weather_forecast, get_driving_distance, get_mandi_price
from api.schemas import NegotiationResult
import json
import time
from datetime import datetime

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
    
    current_date = datetime.now().strftime("%Y-%m-%d") 
    
    print(f"[SYSTEM] Data Secured! Weather: {weather} | Route: {distance}km | Gov Baseline: ₹{mandi_price_ton}/ton\n")

    # 2. Initialize Agents
    agents = AgriAgents()
    farmer = agents.farmer_agent(baseline_price=mandi_price_ton)
    buyer = agents.buyer_agent(commodity=commodity, quantity=quantity_tons, weather=weather)
    transporter = agents.transporter_agent(distance=distance, weather=weather)
    arbitrator = agents.arbitrator_agent()

    # ==========================================
    # 3. DEFINE TASKS
    # ==========================================
    farmer_task = Task(
        description=f"Propose your initial selling price for {quantity_tons} tons of {commodity}. Base market price is ₹{mandi_price_ton}/ton. Justify your price based on labor. MUST quote PER TON.",
        expected_output="A clear initial price offer PER TON from the Farmer.",
        agent=farmer
    )

    transporter_task = Task(
        description=f"Provide your freight quote for the {distance}km journey for a {quantity_tons} ton truckload. Factor in the current weather: '{weather}'. MUST quote the rate PER KM and the TOTAL flat fee for the whole trip.",
        expected_output="A clear rate PER KM and a TOTAL flat freight rate from the Transporter.",
        agent=transporter
    )

    buyer_task = Task(
        description=f"Review the Farmer's crop price (Per Ton) and the Transporter's freight quote (Total Flat Fee). Negotiate aggressively. Provide your counter-offer PER TON for the crop.",
        expected_output="A strict counter-offer to both the Farmer and Transporter.",
        agent=buyer
    )

    # THE LEASH: Strict rules added to stop the Lite model from writing essays
    finalize_task = Task(
        description=(
            f"Review the quotes. Today's date is {current_date}. Mediate a final compromise.\n"
            "CRITICAL UNIT RULES:\n"
            "1. 'farmer_quote' and 'buyer_quote' MUST be expressed as PER TON prices.\n"
            "2. 'transporter_per_km_rate' MUST be the final agreed rate PER KILOMETER.\n"
            "3. 'transporter_quote' MUST be expressed as the TOTAL flat fee for the whole trip.\n"
            "4. 'final_accepted_price' MUST be the agreed CROP price PER TON, do not add freight to this specific number.\n"
            f"5. In the 'contract_text', state the total Landed Cost (Crop price per ton * {quantity_tons}) + Transporter Flat Fee. Use today's date ({current_date}) in the contract.\n"
            "6. 'agent_reasoning_log' must explain the spread between the Farmer and Buyer per-ton quotes before the final median was chosen.\n"
            "7. STRICT RULE: Keep the 'agent_reasoning_log' extremely concise (maximum 3 sentences).\n"
            "8. STRICT RULE: Output ONLY raw JSON data. Do NOT use markdown code blocks (```json) under any circumstances."
        ),
        expected_output="Strict JSON object with standardized units and final contract text.",
        agent=arbitrator,
        output_json=NegotiationResult 
    )

    # 4. Assemble and Run Sequence
    negotiation_crew = Crew(
        agents=[farmer, transporter, buyer, arbitrator],
        tasks=[farmer_task, transporter_task, buyer_task, finalize_task],
        process=Process.sequential, 
        max_rpm=1,  
        step_callback=api_throttle, 
        verbose=True
    )

    print("--- Initiating AI Agent Negotiation Sequence ---")
    result = negotiation_crew.kickoff()
    
    # ==========================================
    # 5. THE MARKDOWN SCRUBBER
    # ==========================================
    if hasattr(result, 'pydantic') and result.pydantic:
        return result.pydantic.model_dump()
    elif hasattr(result, 'json_dict') and result.json_dict:
        return result.json_dict
    else:
        # If the Lite model hallucinates markdown tags, this manually deletes them
        raw_text = result.raw.strip()
        
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:]
            
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
            
        raw_text = raw_text.strip()
        
        try:
            return json.loads(raw_text)
        except Exception as e:
            print(f"\n[PARSING ERROR] Failed to clean JSON. Raw Output was:\n{raw_text}")
            return {"error": "Failed to parse JSON output", "raw": raw_text}