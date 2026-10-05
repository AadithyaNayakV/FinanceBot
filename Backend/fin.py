import os
import numpy as np
from dotenv import load_dotenv

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "")

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

from fileHandling import process
from reddis import data_save_in_cache, data_in_cache
from web_rag import web_search_pipeline

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BACKEND_DIR, "Data")
VECTOR_DB_PATH = os.path.join(BACKEND_DIR, "vector_db")

# Single shared embeddings model
embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def pdf_data():
    loader = PyPDFDirectoryLoader(DATA_DIR)
    return loader.load()

def embed(persist=True):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        add_start_index=True
    )
    docs = pdf_data()
    all_splits = text_splitter.split_documents(docs)

    db = Chroma.from_documents(
        documents=all_splits,
        embedding=embeddings_model,
        persist_directory=VECTOR_DB_PATH if persist else None
    )
    return db

def load_vector_db():
    if os.path.exists(VECTOR_DB_PATH):
        print("[INFO] Loading persisted vector DB from disk...")
        return Chroma(persist_directory=VECTOR_DB_PATH, embedding_function=embeddings_model)
    else:
        print("[INFO] No persisted DB found. Creating new embeddings...")
        return embed(persist=True)

perm_db = load_vector_db()
print(f"[INFO] Vector count in internal DB: {perm_db._collection.count()}")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

# In-memory session cache for the active uploaded document
_active_uploaded_doc = None

GREETING_WORDS = {
    "hi", "hello", "hey", "hola", "namaste", "greetings", "good morning",
    "good afternoon", "good evening", "howdy", "sup", "yo"
}
COURTESY_WORDS = {
    "thanks", "thank you", "thx", "appreciate it", "great", "cool",
    "ok", "okay", "bye", "goodbye", "see you"
}
IDENTITY_WORDS = {
    "who are you", "what are you", "what can you do", "help",
    "how does this work", "how do you work", "what is finbot", "who is finbot"
}

WEB_SEARCH_INDICATORS = [
    "news", "latest", "today", "yesterday", "current", "stock price", "market price",
    "recent", "what happened to", "trending", "live", "search web", "google search"
]

def check_conversational(query: str):
    q = query.lower().strip().rstrip("!?.,")
    if q in GREETING_WORDS or any(q.startswith(g + " ") for g in GREETING_WORDS):
        return (
            "Hello! I am FinBot, your intelligent financial assistant. How can I assist you today? "
            "You can upload financial documents (PDFs, reports, balance sheets, question sets) for in-depth analysis, "
            "or ask questions about market concepts, valuation, and finance.",
            "FinBot"
        )
    if q in COURTESY_WORDS:
        return (
            "You're very welcome! Let me know if you would like me to analyze another document or answer any other financial questions.",
            "FinBot"
        )
    if any(q == w or q.startswith(w) for w in IDENTITY_WORDS):
        return (
            "I am FinBot — an AI financial intelligence assistant designed to help you analyze "
            "financial statements, answer quantitative and qualitative finance questions from your uploaded PDFs, "
            "and explain financial concepts, ratios, and valuation methods.",
            "FinBot"
        )
    return None

def is_web_search_appropriate(query: str) -> bool:
    q = query.lower()
    return any(ind in q for ind in WEB_SEARCH_INDICATORS)

def llm(query: str, files: list = None):
    global _active_uploaded_doc
    llm_model = ChatGoogleGenerativeAI(model=GEMINI_MODEL)
    clean_query = query.strip() if query else ""

    # ----------------------------
    # 0️⃣ GREETINGS & INTRODUCTIONS (NO WEB SEARCH)
    # ----------------------------
    conv_response = check_conversational(clean_query)
    if conv_response and not files:
        return conv_response

    # ----------------------------
    # 1️⃣ INGEST NEW UPLOADED FILES IF PROVIDED
    # ----------------------------
    if files:
        valid_files = [f for f in files if f is not None]
        if valid_files:
            print(f"[INFO] Ingesting {len(valid_files)} uploaded file(s)...")
            doc_data = process(valid_files, embedding_model=embeddings_model)
            if doc_data:
                _active_uploaded_doc = doc_data
                print(f"[INFO] Active uploaded document set: {doc_data['filenames']}")

    # ----------------------------
    # 2️⃣ TIER 1: ACTIVE UPLOADED DOCUMENT (FIRST PRIORITY)
    # ----------------------------
    if _active_uploaded_doc:
        doc_data = _active_uploaded_doc
        source_label = f"Uploaded Document ({', '.join(doc_data['filenames'])})"

        # If user uploaded document with empty query, provide executive overview
        effective_query = clean_query if clean_query else "Provide a comprehensive summary of this document, detailing all questions, sections, and financial metrics."

        print(f"[INFO] Tier 1: Querying uploaded document '{', '.join(doc_data['filenames'])}' (chars: {doc_data['total_chars']})...")

        if doc_data["total_chars"] <= 120000:
            prompt = f"""You are FinBot — an expert financial document intelligence assistant.
Analyze the following uploaded document carefully to answer the user's question accurately.

Uploaded Document(s): {', '.join(doc_data['filenames'])}
=================== DOCUMENT CONTENT START ===================
{doc_data['full_text']}
==================== DOCUMENT CONTENT END ====================

User Question: {effective_query}

Strict Rules:
1. If the user's question CAN be answered using the content in the document (including questions about assessment questions, structural questions like 'what is the first question', question numbers, financial metrics, formulas, or text):
   Answer directly, accurately, and thoroughly based on the document text.
2. If the user's question asks for information completely ABSENT from or UNRELATED to this document (such as current live market prices today, live news, or financial concepts not mentioned anywhere in this document):
   Respond with EXACTLY '[NOT_IN_DOCUMENT]' on the first line, followed by a one-sentence note of what was requested. Do NOT make up information that is not in the document.
Answer:"""
            res = llm_model.invoke(prompt)
            content = res.content
            if isinstance(content, list):
                content = "".join(str(part) for part in content)
            ans_str = str(content).strip()

            if not ans_str.startswith("[NOT_IN_DOCUMENT]"):
                print("[INFO] Answer found in Tier 1: Uploaded Document")
                return ans_str, source_label
            else:
                print(f"[INFO] Query not in uploaded document. Falling back to Tier 2 (Knowledge Base)...")
        else:
            # For massive documents (>120k chars), combine intro overview + vector search chunks
            retriever = doc_data["vector_db"].as_retriever(search_kwargs={"k": 6})
            retrieved_docs = retriever.invoke(effective_query)
            context_text = "\n\n".join([d.page_content for d in retrieved_docs])
            intro_text = doc_data["full_text"][:4000]

            prompt = f"""You are FinBot — an expert financial document intelligence assistant.
Answer the user's question based on the provided document excerpts.

Document: {', '.join(doc_data['filenames'])}
[Document Introduction / Beginning]:
{intro_text}

[Relevant Excerpts]:
{context_text}

User Question: {effective_query}

Strict Rules:
1. If answerable from these excerpts, answer thoroughly.
2. If not mentioned anywhere in these excerpts, respond with EXACTLY '[NOT_IN_DOCUMENT]'.
Answer:"""
            res = llm_model.invoke(prompt)
            content = res.content
            if isinstance(content, list):
                content = "".join(str(part) for part in content)
            ans_str = str(content).strip()

            if not ans_str.startswith("[NOT_IN_DOCUMENT]"):
                print("[INFO] Answer found in Tier 1: Uploaded Document")
                return ans_str, source_label
            else:
                print(f"[INFO] Query not in uploaded document. Falling back to Tier 2 (Knowledge Base)...")

    if not clean_query:
        return "Please ask a financial question or upload a financial document.", "FinBot"

    # ----------------------------
    # 3️⃣ CHECK SEMANTIC CACHE
    # ----------------------------
    cached = data_in_cache(clean_query)
    if cached:
        print("[INFO] Answer retrieved from cache")
        if isinstance(cached, list):
            cached = "".join(str(part) for part in cached)
        return str(cached), "Cache"

    # ----------------------------
    # 4️⃣ TIER 2: INTERNAL KNOWLEDGE BASE (SECOND PRIORITY)
    # ----------------------------
    print(f"[INFO] Tier 2: Searching Internal Knowledge Base for: '{clean_query}'...")
    docs = perm_db.similarity_search_with_score(clean_query, k=2)
    best_score = docs[0][1] if docs else 999.0
    print(f"[INFO] Internal Knowledge Base best distance score: {best_score}")

    qa_prompt = PromptTemplate(
        template="""You are FinBot — an intelligent financial knowledge assistant.
Answer the question strictly using the provided context from the internal finance knowledge base.
If the context does not contain the answer, respond with EXACTLY:
"NOT_IN_KB"

Context: {context}
Question: {question}
Answer:""",
        input_variables=["context", "question"],
    )

    if docs and best_score <= 1.15:
        rag_chain = RetrievalQA.from_chain_type(
            llm=llm_model,
            retriever=perm_db.as_retriever(search_kwargs={"k": 2}),
            chain_type="stuff",
            chain_type_kwargs={"prompt": qa_prompt},
        )
        res_obj = rag_chain.invoke({"query": clean_query})
        response = res_obj.get("result", "") if isinstance(res_obj, dict) else res_obj
        if isinstance(response, list):
            response = "".join(str(part) for part in response)
        response_str = str(response).strip()

        if "NOT_IN_KB" not in response_str and "outside the financial context" not in response_str.lower():
            data_save_in_cache(clean_query, response_str)
            print("[INFO] Answer found in Tier 2: Internal Knowledge Base")
            return response_str, "Internal Knowledge Base"

    print("[INFO] Not in Internal Knowledge Base. Falling back to Tier 3 (Web Search)...")

    # ----------------------------
    # 5️⃣ TIER 3: WEB SEARCH (THIRD PRIORITY)
    # ----------------------------
    print(f"[INFO] Tier 3: Executing Web Search for: '{clean_query}'...")
    try:
        answer, sources = web_search_pipeline(clean_query)
        if isinstance(answer, list):
            answer = "".join(str(part) for part in answer)
        answer_str = str(answer).strip()

        negatives = ["couldn't find", "could not find", "no relevant", "error searching", "cannot find"]
        if answer_str and not any(neg in answer_str.lower() for neg in negatives):
            source_label = f"Web Search ({', '.join(sources[:2])})" if sources else "Web Search"
            data_save_in_cache(clean_query, answer_str)
            print(f"[INFO] Answer found in Tier 3: {source_label}")
            return answer_str, source_label
    except Exception as e:
        print(f"[WARN] Web search execution error: {e}")

    # ----------------------------
    # 6️⃣ FALLBACK: FINBOT GENERAL FINANCIAL AI (GEMINI)
    # ----------------------------
    print("[INFO] Answering via FinBot General Financial AI (Gemini)...")
    direct_prompt = f"""You are FinBot — an intelligent financial knowledge assistant.
Answer the following financial question with accurate financial principles, formulas, definitions, or reasoning.
If the question is completely outside finance and business, respond:
"Sorry, this question is outside the financial context I was trained on."

Question: {clean_query}
Answer:"""
    res = llm_model.invoke(direct_prompt)
    content = res.content
    if isinstance(content, list):
        content = "".join(str(part) for part in content)
    response = str(content).strip()

    data_save_in_cache(clean_query, response)
    return response, "FinBot Financial AI"