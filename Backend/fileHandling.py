
# Load embedder once
# embedder = SentenceTransformer("all-MiniLM-L6-v2")

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from PIL import Image
import pytesseract
from PyPDF2 import PdfReader
import io

def process(uploaded_files: list):
    if not uploaded_files:
        return None

    all_text = ""
    for file in uploaded_files:
        if file.filename.lower().endswith(".pdf"):
            all_text += extract_pdf(file)
        else:
            all_text += extract_image_file(file)

    if not all_text.strip():
        return None

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    splits = text_splitter.create_documents([all_text])
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    temp_vector = Chroma.from_documents(splits, embeddings)
    return temp_vector



def extract_pdf(uploaded_file):
    reader = PdfReader(io.BytesIO(uploaded_file.file.read()))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.strip()



def extract_image_file(uploaded_file):
    image = Image.open(io.BytesIO(uploaded_file.file.read()))
    return pytesseract.image_to_string(image).strip()

