from fastapi import FastAPI, UploadFile, File, Form
from typing import List, Optional
from fin import llm
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="FinanceBot API")

# Universal CORS support for all clients and ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
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
async def chat(
    query: str = Form(""),
    files: Optional[List[UploadFile]] = File(None)
):
    processed_files = []
    if files:
        for f in files:
            if f and f.filename:
                try:
                    content = await f.read()
                    if content:
                        processed_files.append({
                            "filename": f.filename,
                            "content": content,
                            "content_type": f.content_type
                        })
                except Exception as e:
                    print(f"[WARN] Error reading uploaded file {f.filename}: {e}")

    res, source = llm(query=query, files=processed_files if processed_files else None)
    return {"answer": res, "source": source}


@app.post("/reset")
def reset_session():
    import fin
    fin._active_uploaded_doc = None
    return {"status": "ok", "message": "Active document session reset"}

# Optional Gradio interface if installed
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
    # Mount Gradio UI at /gradio to avoid conflicting with root API
    app = gr.mount_gradio_app(app, demo, path="/gradio")
except Exception as e:
    print(f"[INFO] Gradio interface note: {e}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
