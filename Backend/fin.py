from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_google_genai import GoogleGenerativeAIEmbeddings 
from langchain import hub
from langchain_community.embeddings import HuggingFaceEmbeddings

from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma

from langchain_community.document_loaders import PyPDFDirectoryLoader
from dotenv import load_dotenv
load_dotenv()
import os
os.environ["GOOGLE_API_KEY"]=os.getenv('GOOGLE_API_KEY')
from langchain_community.document_loaders import PyPDFLoader
from fileHandling import *
from langchain.retrievers import MultiRetrievalQA


def pdf_data():
    file_path = "./Data"
    loader = PyPDFDirectoryLoader(file_path)
    return loader.load()

def embed():
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=100, 
        add_start_index=True, 
    )
    docs=pdf_data()

    all_splits = text_splitter.split_documents(docs)

    # print(f"Split blog post into {len(all_splits)} sub-documents.")

    embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # embeddings = embeddings_model.embed_documents(
    # docs
    # )
    return Chroma.from_documents(all_splits, embeddings_model)

perm_db=embed()
def llm(query:str,files:list)->str:
    if files:
        temp_db=process(files)

    llm_model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

     # 🧠 Combine both retrievers
    retrievers = [perm_db.as_retriever()]
    if temp_db:
        retrievers.append(temp_db.as_retriever())

    combined_retriever = retrievers[0]
    if len(retrievers) > 1:
        # merge logic: prioritize temp then base
        combined_retriever = MultiRetrievalQA(retrievers=retrievers)

    rag_chain = RetrievalQA.from_chain_type(llm=llm_model, retriever=combined_retriever)
    return rag_chain.run(query)

