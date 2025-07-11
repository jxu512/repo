from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

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
    use_rag: bool = False

class IndexRequest(BaseModel):
    texts: list[str]

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        llm = Ollama(model=req.model)
        if req.use_rag:
            embeddings = OllamaEmbeddings(model=req.model)
            vectorstore = FAISS.load_local("../rag/index", embeddings, allow_dangerous_deserialization=True)
            docs = vectorstore.similarity_search(req.prompt, k=3)
            context = "\n".join([doc.page_content for doc in docs])
            augmented_prompt = f"Context: {context}\n\nQuestion: {req.prompt}"
            response = llm.invoke(augmented_prompt)
        else:
            response = llm.invoke(req.prompt)
        return {"response": response}
    except Exception as e:
        return {"response": f"Error: {str(e)}"}

@app.post("/index")
async def index(req: IndexRequest):
    try:
        documents = [Document(page_content=t) for t in req.texts]
        embeddings = OllamaEmbeddings(model="llama3")
        vectorstore = FAISS.from_documents(documents, embeddings)
        vectorstore.save_local("../rag/index")
        return {"status": "Indexing completed"}
    except Exception as e:
        return {"status": f"Error: {str(e)}"}

# Start server if executed directly
if __name__ == "__main__":
    uvicorn.run("main_w_langchain:app", host="127.0.0.1", port=8000, reload=False)
