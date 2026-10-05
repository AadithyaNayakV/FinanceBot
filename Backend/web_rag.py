import os
import requests
import trafilatura
from urllib.parse import urlparse
from serpapi import GoogleSearch

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# -----------------------------
# CONFIG
# -----------------------------

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

TRUSTED_DOMAINS = [
    "reuters.com",
    "bloomberg.com",
    "investopedia.com",
    "sec.gov",
    "rbi.org.in",
    "moneycontrol.com",
    "economictimes.indiatimes.com"
]

_embeddings = None
_llm = None

def get_web_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return _embeddings

def get_web_llm():
    global _llm
    if _llm is None:
        model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
        _llm = ChatGoogleGenerativeAI(model=model)
    return _llm

# -----------------------------
# 1️⃣ Rewrite Query
# -----------------------------

def rewrite_query(user_question: str) -> str:
    """
    Use LLM to rewrite into optimized search query.
    """
    try:
        prompt = f"""
Rewrite the following question into a concise Google search query.
Question: {user_question}
Search Query:
"""
        response = get_web_llm().invoke(prompt)
        content = response.content
        if isinstance(content, list):
            content = "".join(str(part) for part in content)
        return str(content).strip()
    except Exception as e:
        print(f"[WARN] Error rewriting query: {e}")
        return user_question

# -----------------------------
# 2️⃣ Search Using SerpAPI
# -----------------------------

def search_google(query: str):
    if not SERPAPI_KEY:
        print("[WARN] SERPAPI_KEY is not configured.")
        return [], []
    try:
        params = {
            "engine": "google",
            "q": query,
            "api_key": SERPAPI_KEY,
            "num": 5
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        links = []
        snippets = []
        for item in results.get("organic_results", []):
            link = item.get("link")
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            if link:
                links.append(link)
                if snippet:
                    snippets.append(f"Title: {title}\nURL: {link}\nSnippet: {snippet}")

        return links, snippets
    except Exception as e:
        print(f"[WARN] SerpAPI search error: {e}")
        return [], []

# -----------------------------
# 3️⃣ Domain Filter
# -----------------------------

def filter_domains(links):
    filtered = []
    for link in links:
        domain = urlparse(link).netloc
        if any(trusted in domain for trusted in TRUSTED_DOMAINS):
            filtered.append(link)
    return filtered

# -----------------------------
# 4️⃣ Safe Scraper
# -----------------------------

def scrape_article(url: str):
    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=5
        )

        if response.status_code != 200:
            return None

        extracted = trafilatura.extract(response.text)

        if not extracted or len(extracted) < 500:
            return None

        return extracted

    except Exception:
        return None

# -----------------------------
# 5️⃣ Embed Web Content
# -----------------------------

def embed_web_content(text_list):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )

    documents = splitter.create_documents(text_list)
    temp_db = Chroma.from_documents(documents, get_web_embeddings())
    return temp_db

# -----------------------------
# 6️⃣ Generate Answer from Web Context
# -----------------------------

def generate_web_answer(user_question, temp_db):
    qa_prompt = PromptTemplate(
        template="""
You are a financial assistant.
Answer strictly using the provided web context.
Do not invent information.

Context:
{context}

Question:
{question}

Answer:
""",
        input_variables=["context", "question"]
    )

    rag_chain = RetrievalQA.from_chain_type(
        llm=get_web_llm(),
        retriever=temp_db.as_retriever(),
        chain_type="stuff",
        chain_type_kwargs={"prompt": qa_prompt}
    )

    res_obj = rag_chain.invoke({"query": user_question})
    ans = res_obj.get("result", "") if isinstance(res_obj, dict) else res_obj
    if isinstance(ans, list):
        ans = "".join(str(part) for part in ans)
    return str(ans)

# -----------------------------
# 🚀 MAIN WEB PIPELINE
# -----------------------------

def web_search_pipeline(user_question: str):
    try:
        print("[INFO] Rewriting query...")
        search_query = rewrite_query(user_question)

        print(f"[INFO] Searching Google for: {search_query}")
        links, snippets = search_google(search_query)

        collected_articles = []
        sources = []

        for link in links:
            print(f"[INFO] Scraping: {link}")
            article = scrape_article(link)

            if article:
                collected_articles.append(article)
                sources.append(link)

            if len(collected_articles) >= 3:
                break

        if not collected_articles:
            if snippets:
                print("[INFO] Using Google search snippets directly...")
                llm = get_web_llm()
                snippet_context = "\n\n".join(snippets[:5])
                prompt = f"""You are FinBot — an expert financial research assistant.
Answer the user's question using the following search snippets from Google.
Keep it factual, helpful, and concise.

Context:
{snippet_context}

Question: {user_question}
Answer:"""
                res = llm.invoke(prompt)
                content = res.content
                if isinstance(content, list):
                    content = "".join(str(part) for part in content)
                return str(content).strip(), links[:3]
            return "I couldn't find relevant financial information from the web search.", []

        print("[INFO] Embedding web content...")
        temp_db = embed_web_content(collected_articles)

        print("[INFO] Generating answer...")
        answer = generate_web_answer(user_question, temp_db)

        return answer, sources
    except Exception as e:
        print(f"[WARN] Web search pipeline failed: {e}")
        return f"Error searching the web: {e}", []