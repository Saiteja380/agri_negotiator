from fastapi import APIRouter, HTTPException
from api.schemas import NegotiationRequest
from agents.orchestrator import run_negotiation
from core.db import save_contract_to_db

router = APIRouter()

@router.post("/api/v1/negotiate")
def trigger_negotiation(request: NegotiationRequest):
    print(f"\n[WEB SERVER] Incoming request received for {request.quantity_tons} tons of {request.commodity}...")
    
    try:
        # 1. Pass the web data directly into your AI orchestrator
        structured_result = run_negotiation(
            commodity=request.commodity,
            state=request.state,
            start_lat=request.start_lat,
            start_lon=request.start_lon,
            end_lat=request.end_lat,
            end_lon=request.end_lon,
            quantity_tons=request.quantity_tons
        )
        
        # 2. Fire the structured data into your Supabase database
        trade_id = save_contract_to_db(
            commodity=request.commodity,
            quantity_tons=request.quantity_tons,
            result_data=structured_result
        )
        
        # 3. Return the payload
        return {
            "status": "success", 
            "trade_id": trade_id,
            "data": structured_result
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"[WEB SERVER] Error during negotiation: {error_msg}")
        
        # Specifically catch the Google API Rate Limit
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            raise HTTPException(status_code=429, detail="API_RATE_LIMIT")
            
        raise HTTPException(status_code=500, detail=error_msg)