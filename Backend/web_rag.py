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

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# -----------------------------
# 1️⃣ Rewrite Query
# -----------------------------

def rewrite_query(user_question: str) -> str:
    """
    Use LLM to rewrite into optimized search query.
    """
    prompt = f"""
Rewrite the following question into a concise Google search query.
Question: {user_question}
Search Query:
"""
    response = llm.invoke(prompt)
    return response.content.strip()

# -----------------------------
# 2️⃣ Search Using SerpAPI
# -----------------------------

def search_google(query: str):
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": 5
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    print("RAW RESULTS:", results)

    links = []
    for item in results.get("organic_results", []):
        link = item.get("link")
        if link:
            links.append(link)

    return links

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

    temp_db = Chroma.from_documents(documents, embeddings)

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
        llm=llm,
        retriever=temp_db.as_retriever(),
        chain_type="stuff",
        chain_type_kwargs={"prompt": qa_prompt}
    )

    return rag_chain.run(user_question)

# -----------------------------
# 🚀 MAIN WEB PIPELINE
# -----------------------------

def web_search_pipeline(user_question: str):

    print("Rewriting query...")
    search_query = rewrite_query(user_question)

    print("Searching Google...")
    links = search_google(search_query)

    print("Filtering domains...")
    # trusted_links = filter_domains(links)
    trusted_links = links

    collected_articles = []
    sources = []

    for link in trusted_links:
        print(f"Scraping: {link}")
        article = scrape_article(link)

        if article:
            collected_articles.append(article)
            sources.append(link)

        if len(collected_articles) >= 3:
            break

    if not collected_articles:
        return "No reliable web sources found.", []

    print("Embedding web content...")
    temp_db = embed_web_content(collected_articles)

    print("Generating answer...")
    answer = generate_web_answer(user_question, temp_db)

    return answer, sources