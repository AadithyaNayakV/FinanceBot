import io
import os
import base64
from PIL import Image
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader

_default_embeddings = None

def get_default_embeddings():
    global _default_embeddings
    if _default_embeddings is None:
        _default_embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return _default_embeddings


def _ocr_page_images_with_gemini(images_data: list, start_page_num: int = 1) -> str:
    """Use Gemini Vision to transcribe images from scanned PDF pages."""
    if not images_data:
        return ""
    try:
        model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
        llm = ChatGoogleGenerativeAI(model=model_name)
        content_parts = [
            {
                "type": "text", 
                "text": "You are an expert document OCR engine. Transcribe ALL questions, text, numbers, formulas, options, and tables from the provided pages exactly. Maintain clear section and page structure."
            }
        ]
        for idx, img_bytes in enumerate(images_data):
            page_num = start_page_num + idx
            im = Image.open(io.BytesIO(img_bytes))
            im.thumbnail((1200, 1200))
            buf = io.BytesIO()
            im.save(buf, format="JPEG", quality=80)
            img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            content_parts.append({"type": "text", "text": f"\n=== PAGE {page_num} ===\n"})
            content_parts.append({"type": "image_url", "image_url": f"data:image/jpeg;base64,{img_b64}"})

        resp = llm.invoke([HumanMessage(content=content_parts)])
        content = resp.content
        if isinstance(content, list):
            content = "".join(str(part) for part in content)
        return str(content).strip()
    except Exception as e:
        print(f"[WARN] Gemini Vision OCR failed: {e}")
        return ""


def process(uploaded_files: list, embedding_model=None):
    if not uploaded_files:
        return None

    embeddings = embedding_model or get_default_embeddings()
    all_chunks = []
    combined_texts = []
    file_names = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)

    for file in uploaded_files:
        if not file:
            continue

        filename = ""
        if isinstance(file, dict):
            filename = file.get("filename", "")
        else:
            filename = getattr(file, "filename", None) or getattr(file, "name", "")
        
        filename_lower = filename.lower()
        extracted_text = ""

        try:
            if filename_lower.endswith(".pdf") or not filename:
                extracted_text = extract_pdf(file)
            elif any(filename_lower.endswith(ext) for ext in [".txt", ".csv", ".json", ".md"]):
                extracted_text = extract_text_file(file)
            else:
                extracted_text = extract_image_file(file)
        except Exception as e:
            print(f"[WARN] Failed to extract from file {filename}: {e}")

        if extracted_text and extracted_text.strip():
            display_name = filename or "uploaded_document"
            file_names.append(display_name)
            combined_texts.append(f"=== Document: {display_name} ===\n{extracted_text.strip()}")

            doc_splits = text_splitter.create_documents(
                texts=[extracted_text.strip()],
                metadatas=[{"source": display_name}]
            )
            all_chunks.extend(doc_splits)
        else:
            print(f"[WARN] No readable text extracted from {filename}")

    if not combined_texts:
        return None

    full_text = "\n\n".join(combined_texts)
    temp_vector = Chroma.from_documents(documents=all_chunks, embedding=embeddings) if all_chunks else None

    return {
        "full_text": full_text,
        "filenames": file_names,
        "vector_db": temp_vector,
        "total_chars": len(full_text),
    }


def _get_bytes(uploaded_file):
    if isinstance(uploaded_file, dict):
        return uploaded_file.get("content", b"")
    if hasattr(uploaded_file, "file"):
        try:
            uploaded_file.file.seek(0)
            return uploaded_file.file.read()
        except Exception:
            pass
    if hasattr(uploaded_file, "read"):
        try:
            content = uploaded_file.read()
            if hasattr(uploaded_file, "seek"):
                try:
                    uploaded_file.seek(0)
                except Exception:
                    pass
            if isinstance(content, (bytes, bytearray)):
                return bytes(content)
        except Exception:
            pass
    elif isinstance(uploaded_file, (bytes, bytearray)):
        return bytes(uploaded_file)
    elif isinstance(uploaded_file, str) and os.path.isfile(uploaded_file):
        with open(uploaded_file, "rb") as f:
            return f.read()
    return b""


def extract_pdf(uploaded_file):
    content = _get_bytes(uploaded_file)
    if not content:
        return ""
    try:
        reader = PdfReader(io.BytesIO(content))
        text_parts = []
        scanned_images = []

        for idx, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text and page_text.strip():
                text_parts.append(f"[Page {idx + 1}]\n{page_text.strip()}")
            elif page.images:
                # Page has no digital text but has images -> scanned page
                scanned_images.append((idx + 1, page.images[0].data))

        # If digital text exists, return it
        combined_digital = "\n\n".join(text_parts).strip()
        if len(combined_digital) >= 50:
            return combined_digital

        # If scanned/image PDF, transcribe pages using Gemini Vision
        if scanned_images:
            print(f"[INFO] Scanned PDF detected ({len(scanned_images)} image pages). Performing Vision OCR...")
            ocr_parts = []
            # Batch in chunks of 5 pages for rapid processing
            batch_size = 5
            for i in range(0, len(scanned_images), batch_size):
                batch = scanned_images[i:i + batch_size]
                batch_imgs = [img_data for _, img_data in batch]
                start_p = batch[0][0]
                batch_text = _ocr_page_images_with_gemini(batch_imgs, start_page_num=start_p)
                if batch_text:
                    ocr_parts.append(batch_text)

            transcribed = "\n\n".join(ocr_parts).strip()
            if transcribed:
                return transcribed

        return combined_digital
    except Exception as e:
        print(f"[WARN] PDF extraction error: {e}")
        return ""


def extract_text_file(uploaded_file):
    content = _get_bytes(uploaded_file)
    if not content:
        return ""
    try:
        return content.decode("utf-8", errors="ignore").strip()
    except Exception as e:
        print(f"[WARN] Text extraction error: {e}")
        return ""


def extract_image_file(uploaded_file):
    content = _get_bytes(uploaded_file)
    if not content:
        return ""
    # Try pytesseract first if installed
    try:
        import pytesseract
        image = Image.open(io.BytesIO(content))
        txt = pytesseract.image_to_string(image).strip()
        if txt:
            return txt
    except Exception:
        pass

    # Fallback to Gemini Vision for image
    try:
        print("[INFO] Performing Gemini Vision OCR on uploaded image...")
        model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
        llm = ChatGoogleGenerativeAI(model=model_name)
        im = Image.open(io.BytesIO(content))
        im.thumbnail((1200, 1200))
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=80)
        img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        msg = HumanMessage(content=[
            {"type": "text", "text": "Extract and transcribe all text, numbers, formulas, and data from this image exactly."},
            {"type": "image_url", "image_url": f"data:image/jpeg;base64,{img_b64}"}
        ])
        resp = llm.invoke([msg])
        content = resp.content
        if isinstance(content, list):
            content = "".join(str(part) for part in content)
        return str(content).strip()
    except Exception as e:
        print(f"[WARN] Image extraction error: {e}")
        return ""

