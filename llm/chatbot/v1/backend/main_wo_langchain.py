# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import uvicorn

app = FastAPI()

# Enable CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    prompt: str
    model: str

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        async with httpx.AsyncClient(timeout=600.0) as client:
            response = await client.post("http://localhost:11434/api/generate", json={
                "model": req.model,
                "prompt": req.prompt,
                "stream": False
            })
            response.raise_for_status()
            data = response.json()
            # Ollama API returns response in 'response' field, not 'message.content'
            message = data.get("response", "No response from model.")
            return {"response": message}
    except httpx.RequestError as e:
        return {"response": f"Error connecting to Ollama: {str(e)}"}
    except httpx.HTTPStatusError as e:
        return {"response": f"HTTP error from Ollama: {e.response.status_code}"}
    except Exception as e:
        return {"response": f"Unexpected error: {str(e)}"}

# Start server if executed directly
if __name__ == "__main__":
    uvicorn.run("main_wo_langchain:app", host="127.0.0.1", port=8000, reload=False)
