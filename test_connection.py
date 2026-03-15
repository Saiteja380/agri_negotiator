from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

print("1. Loading .env file...")
load_dotenv()

print("2. Attempting to connect to Gemini...")
try:
    # 🟢 USING THE CORRECT V1 MODEL FROM YOUR MDD
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    
    # Sending a ping to the AI
    response = llm.invoke("Reply with exactly three words: 'API Connection Successful'.")
    print(f"\n✅ RESULT: {response.content}")

except Exception as e:
    print(f"\n🚨 FAILED: {e}")