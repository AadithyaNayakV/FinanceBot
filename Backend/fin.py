from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_google_genai import GoogleGenerativeAIEmbeddings 
# from langchain import hub
# from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma

from langchain_community.document_loaders import PyPDFDirectoryLoader
from dotenv import load_dotenv
load_dotenv()
import os
os.environ["GOOGLE_API_KEY"]=os.getenv('GOOGLE_API_KEY')
from langchain_community.document_loaders import PyPDFLoader
from fileHandling import *
# from langchain.retrievers import MultiRetrievalQA
from langchain.chains import RetrievalQA
# from langchain_community.retrievers import EnsembleRetriever


# from langchain.chains import create_retrieval_chain
# from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.schema import BaseRetriever, Document

class CombinedRetriever(BaseRetriever):
    retrievers: list[BaseRetriever]

    def get_relevant_documents(self, query: str) -> list[Document]:
        results = []
        for retriever in self.retrievers:
            results.extend(retriever.get_relevant_documents(query))
        return results


VECTOR_DB_PATH = "./vector_db" 

def pdf_data():
    file_path = "./Data"
    loader = PyPDFDirectoryLoader(file_path)
    return loader.load()

def embed(persist=True):
    """
    Embeds PDFs and saves vector DB to disk if persist=True
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        add_start_index=True
    )
    docs = pdf_data()
    all_splits = text_splitter.split_documents(docs)

    embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    db = Chroma.from_documents(
        documents=all_splits,
        embedding=embeddings_model,
        persist_directory=VECTOR_DB_PATH if persist else None
    )

    if persist:
        db.persist()  # saves to disk
        print("Vector DB persisted to disk.")

    return db

def load_vector_db():
    """
    Load vector DB from disk
    """
    embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    if os.path.exists(VECTOR_DB_PATH):
        print("Loading persisted vector DB from disk...")
        return Chroma(persist_directory=VECTOR_DB_PATH, embedding_function=embeddings_model)
    else:
        print("No persisted DB found. Creating new embeddings...")
        return embed(persist=True)
    
perm_db=load_vector_db()

def llm(query:str,files:list)->str:
    if files:
        temp_db=process(files)
    else:
        temp_db = None

    llm_model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

    retrievers = []
    if perm_db:  # your permanent database
        retrievers.append(perm_db.as_retriever())
    if temp_db:  # user-uploaded files
        retrievers.append(temp_db.as_retriever())

    # combined_retriever = CombinedRetriever(retrievers=retrievers)

   
    # if len(retrievers) > 1:
    #     results = []
    #     for r in retrievers:
    #         results.extend(r.get_relevant_documents(query))
    #     return results
        
    # else:
    #     combined_retriever = retrievers[0]
    combined_retriever = CombinedRetriever(retrievers=[perm_db.as_retriever(), temp_db.as_retriever() if temp_db else perm_db.as_retriever()])

    rag_chain = RetrievalQA.from_chain_type(
        llm=llm_model,
        retriever=combined_retriever,
        # return_source_documents=True
    )

    return rag_chain.run(query)

    # question_answer_chain = create_stuff_documents_chain(llm_model)
    # chain = create_retrieval_chain(retriever=combined_retriever,
    #     combine_documents_chain=question_answer_chain)

    # result=chain.invoke({"input": query})
    # return result

