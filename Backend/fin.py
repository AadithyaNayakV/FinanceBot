from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_google_genai import GoogleGenerativeAIEmbeddings 
# from langchain import hub
# from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.document_loaders import PyPDFLoader
from fileHandling import *
# from langchain.retrievers import MultiRetrievalQA
from langchain.chains import RetrievalQA
# from langchain_community.retrievers import EnsembleRetriever

from langchain import hub
# from langchain.chains import create_retrieval_chain
# from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.schema import BaseRetriever, Document
# from langchain.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
load_dotenv()
import os
os.environ["GOOGLE_API_KEY"]=os.getenv('GOOGLE_API_KEY')
import numpy as np
from reddis import *

embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


class CombinedRetriever(BaseRetriever):
    retrievers: list[BaseRetriever]

    def get_relevant_documents(self, query: str) -> list[Document]:
        results = []
        for retriever in self.retrievers:
            results.extend(retriever.get_relevant_documents(query))
        return results


system_template ="""
You are FinBot — an intelligent financial knowledge assistant.
You answer strictly using financial documents or the finance vector DB.
If a question is outside finance, respond:
"Sorry, this question is outside the financial context I was trained on."

Guidelines:
- No special characters like *, #, @, $, %, etc.
- Provide clear, accurate, thoughtful answers.
- Do not invent information not in the documents.
- If answer not in docs, say: "I don't have that information in the context."
- Respond in complete sentences and professional tone.
"""
# system_message_template = SystemMessagePromptTemplate.from_template(system_template)

VECTOR_DB_PATH = "./vector_db" 

def pdf_data():
    file_path = "./Data"
    loader = PyPDFDirectoryLoader(file_path)
    return loader.load()

def embed(persist=True):
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
        db.persist() 
        print("Vector DB persisted to disk.")

    return db

def load_vector_db():
    embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    if os.path.exists(VECTOR_DB_PATH):
        print("Loading persisted vector DB from disk...")
        return Chroma(persist_directory=VECTOR_DB_PATH, embedding_function=embeddings_model)
    else:
        print("No persisted DB found. Creating new embeddings...")
        return embed(persist=True)
    
perm_db=load_vector_db()

def get_embedding(text: str):
    """Convert text to vector"""
    return np.array(embeddings_model.embed_query(text))

def compare(v1, v2):
    get_embedding(v1,v2)
    """Compute cosine similarity between 2 vectors"""
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def llm(query:str,files:list)->str:
    best_ans=None
    source=None
    if files:
        temp_db=process(files)
    else:
        temp_db = None

    llm_model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    qa_prompt = PromptTemplate(
            template="""
        You are FinBot — an intelligent financial knowledge assistant.
        Answer strictly using financial documents or the finance vector DB.
        If a question is outside finance, respond:
        "Sorry, this question is outside the financial context I was trained on."
        Guidelines:
        - No special characters like *, #, @, $, %, etc.
        - Provide clear, accurate, thoughtful answers.
        - Do not invent information not in the documents.
        - If answer not in docs, say: "I don’t have that information in the context."
        - Respond in complete sentences and professional tone.

        Context: {context}
    Question: {question}
        Answer:
        """,
            input_variables=["context", "question"],    # must be "input" in 0.3.x
        )
    if temp_db: 
        retrievers.append(temp_db.as_retriever())
        chat_prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("user", "{question}")
    ])
   
    # prompt = hub.pull("your-prompt-handle")
  
        
        rag_chain = RetrievalQA.from_chain_type(
            llm=llm_model,
            retriever=temp_db,
            chain_type="stuff",
        chain_type_kwargs={"prompt": qa_prompt},
            # return_source_documents=True
        )

        
        response = rag_chain.run(query)
        score=compare(query,response)
        if(score>0.85):
            print("ans frm your file")
            best_ans=response
            source="Your File"
        
    else :
        cc=data_in_cache(query)
        if(cc):
            if compare(query,cc)>0.85:
                print("ans frm your cache")
                best_ans=cc
                source="cache"
        else:
            retrievers = []
            if cc:
                retrievers.append(cc)
            elif perm_db: 
                retrievers.append(perm_db.as_retriever())

            combined_retriever = CombinedRetriever(retrievers=[perm_db.as_retriever(), temp_db.as_retriever() if temp_db else perm_db.as_retriever()])

            chat_prompt_template = ChatPromptTemplate.from_messages([
                ("system", system_template),
                ("user", "{question}")
            ])
        
            # prompt = hub.pull("your-prompt-handle"
            rag_chain = RetrievalQA.from_chain_type(
                llm=llm_model,
                retriever=combined_retriever,
                chain_type="stuff",
            chain_type_kwargs={"prompt": qa_prompt},
                # return_source_documents=True
            )

            
            response = rag_chain.run(query)
            data_save_in_cache(query,response)
            best_ans=response
            source="outside"
            print("ans frm your outside")
            return best_ans,source



