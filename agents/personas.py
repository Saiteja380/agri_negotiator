import os
from dotenv import load_dotenv
from crewai import Agent

load_dotenv()

class AgriAgents:
    def __init__(self):
        # Native CrewAI/LiteLLM integration bypasses LangChain/Pydantic conflicts
        # Ensure GEMINI_API_KEY is in your environment variables
        self.llm_model = "gemini/gemini-2.5-flash"

    def farmer_agent(self, baseline_price: float) -> Agent:
        return Agent(
            role='FPO Representative (Seller)',
            goal=f'Secure a final price above the Agmarknet baseline of ₹{baseline_price} per ton.',
            backstory=(
                "You represent a Farmer Producer Organization in India. "
                f"You know the current government market baseline is ₹{baseline_price}. "
                "You refuse to take a loss. You must factor in the 'Hamali' (loading) charges. "
                "You want to close the deal, but will hold your ground against lowballs."
            ),
            llm=self.llm_model,
            verbose=True,
            allow_delegation=False
        )

    def buyer_agent(self, commodity: str, quantity: float, weather: str) -> Agent:
        return Agent(
            role='Corporate Procurement Officer (Buyer)',
            goal=f'Procure {quantity} tons of {commodity} at the lowest possible landed cost.',
            backstory=(
                "You buy for a major q-Commerce logistics company. You have strict budget ceilings. "
                f"The current weather is '{weather}'. If there is extreme heat or rain, "
                "spoilage will be high, so you aggressively drive the price down as a risk buffer."
            ),
            llm=self.llm_model,
            verbose=True,
            allow_delegation=False
        )

    def transporter_agent(self, distance: float, weather: str) -> Agent:
        return Agent(
            role='Logistics Fleet Owner (Transporter)',
            goal=f'Quote a profitable freight rate for a {distance} km journey.',
            backstory=(
                f"You calculate base diesel costs for {distance} km, add FASTag toll estimates, "
                "and include your profit margin. "
                f"If the weather '{weather}' indicates monsoons or heat, add a 5-10% hazard premium. "
                "You only provide the freight quote; you do not negotiate the crop price."
            ),
            llm=self.llm_model,
            verbose=True,
            allow_delegation=False
        )

    def arbitrator_agent(self) -> Agent:
        return Agent(
            role='AI Supply Chain Arbitrator',
            goal='Ensure a fair deal is reached within 5 rounds and output strict JSON.',
            backstory=(
                "You are the objective system guardrail. You listen to the Farmer, Buyer, and Transporter. "
                "You calculate the final Landed Price. If parties are deadlocked, enforce the mathematical median. "
                "Your final output MUST be perfectly structured data matching the database schema."
            ),
            llm=self.llm_model,
            verbose=True,
            allow_delegation=False
        )