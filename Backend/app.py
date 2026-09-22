from fastapi import FastAPI, UploadFile, File, Form
from typing import List,Optional
from fin import llm
from fastapi.middleware.cors import CORSMiddleware

import os

app = FastAPI(title="FinanceBot API")

# Allow CORS for localhost and deployed frontend (e.g. Vercel)
cors_origins_env = os.getenv("CORS_ORIGINS", "*")
origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_origin_regex=r".*" if origins == ["*"] else None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "FinanceBot Backend is active"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/chat")
async def chat(query: str = Form(...),  files: Optional[List[UploadFile]] = File(None) ):
    res,source = llm(query=query, files=files)
    return {"answer": res,"source":source}

# Mount Gradio interface for Hugging Face Spaces Gradio SDK
try:
    import gradio as gr

    def gradio_chat(user_message, history):
        ans, src = llm(query=user_message, files=None)
        return ans

    demo = gr.ChatInterface(
        fn=gradio_chat,
        title="FinanceBot AI",
        description="FinanceBot Backend & AI Engine. You can interact here or via your Vercel frontend."
    )
    # Mount Gradio UI at root /
    app = gr.mount_gradio_app(app, demo, path="/")
except Exception as e:
    print(f"Gradio interface initialization note: {e}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
