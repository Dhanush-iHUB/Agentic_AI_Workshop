from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.persona_detection_agent import PersonaDetectionAgent
import uvicorn
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Allow CORS for all origins (for Postman testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PersonaRequest(BaseModel):
    content: str

# Initialize the agent
persona_agent = PersonaDetectionAgent()

@app.post("/detect_persona")
def detect_persona(request: PersonaRequest):
    result = persona_agent.process(request.content)
    return result

if __name__ == "__main__":
    uvicorn.run("agent_api:app", host="0.0.0.0", port=8000, reload=True) 