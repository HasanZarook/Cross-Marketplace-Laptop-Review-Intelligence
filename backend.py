
import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq  # Groq SDK
from dotenv import load_dotenv
from src.tools.webpage_scraper2 import get_final_output  # Your previously scraped HTML
# from src.tools.webpage_scraper import run_all  # Import the scraper function

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not set in .env file")

# Initialize FastAPI
app = FastAPI(title="Laptop Assistant API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory chat history (store as dict for proper message format)
chat_history: list[dict] = []

# Pydantic model for incoming chat requests
class ChatRequest(BaseModel):
    question: str

def load_pdf_specs() -> str:
    """Load PDF specs JSON and convert to string for LLM prompt."""
    json_path = os.path.join(os.path.dirname(__file__), "laptop_specs_normalized.json")
    with open(json_path, "r", encoding="utf-8") as file:
        pdf_specs_data = json.load(file)
    return json.dumps(pdf_specs_data, indent=2)

def load_web_scrap() -> str:
    """Load PDF specs JSON and convert to string for LLM prompt."""
    json_path = os.path.join(os.path.dirname(__file__), "laptops_output.json")
    with open(json_path, "r", encoding="utf-8") as file:
        pdf_specs_data = json.load(file)
    return json.dumps(pdf_specs_data, indent=2)

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Chat endpoint to answer user questions about 4 specific laptops.
    """
    question = request.question.strip()
    if not question:
        return {"answer": "Hello! How can I help you with the 4 laptops?"}

    pdf_specs_string = load_pdf_specs()
    
    # webfinal_output = await run_all()
    webfinal_output_2 = get_final_output()
    webfinal_output = load_web_scrap()
    # System prompt with instructions
    system_prompt = f"""
You are an expert Business Laptop Assistant.

Laptop Options (ONLY these 4):
1. Lenovo ThinkPad E14 Gen5 Intel
2. Lenovo ThinkPad E14 Gen5 AMD
3. HP ProBook 450 15.6 inch G10 Notebook PC
4. HP ProBook 440 14 inch G11 Notebook PC

Data Sources:
1. PDF Specs: {pdf_specs_string}
2. Website Scrap Data: {webfinal_output_2} {webfinal_output}


Instructions:
1. ONLY answer questions about the 4 laptops above.
2. ALWAYS check both PDF Specs and Website scrapdata to find information.
3. If a laptop is missing from the website scrapdata but present in PDF, use the PDF data.
4. NEVER invent or assume any specs.
5. Provide structured answers in the following format:
   - **Laptop Name:**
   - **Key Specifications:** (CPU, RAM, Storage, Display, GPU, Battery, etc.)
   - **Current Price:** (extract from website scrapdata)
   - **Pros:** 
   - **Cons:** 
   - **Recommendation:** 

IMPORTANT:
- If the question is about something outside the 4 laptops, say "out of scope."
- If the user just greets, greet back.
"""

    # Build messages array for the API
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add chat history
    messages.extend(chat_history)
    
    # Add current user question
    messages.append({"role": "user", "content": question})

    try:
        # Call Groq API with correct method
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # No "groq/" prefix needed
            messages=messages,
            temperature=0,
            max_tokens=2000
        )
        
        assistant_message = response.choices[0].message.content.strip()
        
        # Update chat history
        chat_history.append({"role": "user", "content": question})
        chat_history.append({"role": "assistant", "content": assistant_message})
        
        # Keep only last 10 messages to avoid context length issues
        if len(chat_history) > 10:
            chat_history[:] = chat_history[-10:]
        
        return {"answer": assistant_message}
    
    except Exception as e:
        return {"answer": f"Error: {str(e)}"}

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "API is running"}

@app.post("/clear")
async def clear_history():
    """Clear chat history."""
    chat_history.clear()
    return {"status": "Chat history cleared"}
