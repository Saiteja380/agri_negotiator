import asyncio
from fastapi import FastAPI
from api.routes import router
from core.data_fetcher import update_agmarket_cache, get_dynamic_agmarket_lists

# Initialize the main FastAPI application
app = FastAPI(title="Agri-Negotiator API")

# Connect the routes from api/routes.py
app.include_router(router)

async def periodic_data_fetch(interval_seconds: int):
    """An infinite loop that runs silently in the background."""
    while True:
        update_agmarket_cache()
        # Sleep for the designated interval before fetching again
        await asyncio.sleep(interval_seconds)

@app.on_event("startup")
async def startup_event():
    """Fires exactly once when the Docker container boots up."""
    print("🚀 Starting Background Workers...")
    # Start the periodic fetcher to run every 3600 seconds (1 Hour)
    asyncio.create_task(periodic_data_fetch(3600))

@app.get("/")
def read_root():
    return {"message": "Agri-Negotiator API is running smoothly!"}

@app.get("/api/v1/reference-data")
def get_reference_data():
    """UI hits this endpoint and gets an instant response from the RAM cache."""
    states, commodities = get_dynamic_agmarket_lists()
    return {"states": states, "commodities": commodities}