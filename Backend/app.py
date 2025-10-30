from fastapi import FastAPI, UploadFile, File, Form
from typing import List,Optional
from fin import llm
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:5173",  # your frontend URL
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(query: str = Form(...),  files: Optional[List[UploadFile]] = File(None) ):
    
    res,source = llm(query=query, files=files)
    return {"answer": res,"source":source}
