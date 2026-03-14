from fastapi import FastAPI
from api.routes import router

# Initialize the main FastAPI application
app = FastAPI(title="Agri-Negotiator API")

# Connect the routes from api/routes.py
app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Agri-Negotiator API is running smoothly!"}