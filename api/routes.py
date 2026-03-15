from fastapi import APIRouter, HTTPException
from api.schemas import NegotiationRequest
from agents.orchestrator import run_negotiation
from core.db import save_contract_to_db

router = APIRouter()

@router.post("/api/v1/negotiate", status_code=200)
def trigger_negotiation(request: NegotiationRequest):
    """
    Receives trade parameters from the Streamlit UI, triggers the CrewAI negotiation,
    and logs the deterministically verified contract to Supabase.
    """
    print(f"\n[API ROUTER] 🟢 Incoming B2B Negotiation Request: {request.quantity_tons}T of {request.commodity}")
    
    try:
        # 1. Trigger the AI Crew and Deterministic Math Engine
        structured_result = run_negotiation(
            commodity=request.commodity,
            state=request.state,
            start_lat=request.start_lat,
            start_lon=request.start_lon,
            end_lat=request.end_lat,
            end_lon=request.end_lon,
            quantity_tons=request.quantity_tons
        )
        
        # 2. Verify the Math Override successfully executed before hitting the DB
        if not structured_result.get("math_verified"):
            print("[API ROUTER] ⚠️ WARNING: Math verification flag missing from engine output!")
        else:
            print(f"[API ROUTER] 🔒 Verified True Landed Cost: ₹{structured_result.get('true_landed_cost'):,.2f}")

        # 3. Log the verified contract into Supabase
        # (We will update the db.py logic next to handle these new fields)
        trade_id = save_contract_to_db(
            commodity=request.commodity,
            quantity_tons=request.quantity_tons,
            result_data=structured_result
        )
        
        # 4. Return the final payload to the Streamlit UI
        print(f"[API ROUTER] ✅ Payload successfully routed to DB (ID: {trade_id}) and Frontend.")
        return {
            "status": "success", 
            "trade_id": trade_id,
            "data": structured_result
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"\n[API ROUTER] 🚨 Critical Error during negotiation: {error_msg}")
        
        # Specifically catch the Google Gemini Free Tier Rate Limit
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            raise HTTPException(status_code=429, detail="GEMINI_API_RATE_LIMIT_EXCEEDED")
            
        raise HTTPException(status_code=500, detail=error_msg)