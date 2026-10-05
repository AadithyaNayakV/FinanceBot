"""
Test script to verify FinanceBot PDF Question-Answering.
Run this with:
    cd Backend
    .\venv\Scripts\python.exe test_dummy_pdf.py
"""
import os
import io
import sys
from fin import llm

class MockUploadFile:
    def __init__(self, filepath):
        self.filename = os.path.basename(filepath)
        with open(filepath, "rb") as f:
            self._content = f.read()
        self.file = io.BytesIO(self._content)

    def read(self):
        return self._content

def main():
    pdf_path = os.path.join(os.path.dirname(__file__), "dummy_financial_report.pdf")
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found.")
        sys.exit(1)

    print("=" * 60)
    print("Testing FinanceBot with Dummy PDF: dummy_financial_report.pdf")
    print("=" * 60)

    test_queries = [
        "What is the total revenue of Acme Corp in Q3 2026?",
        "What is the Net Income / Profit and EPS?",
        "What is the guidance for Q4 2026?"
    ]

    for query in test_queries:
        print(f"\n[USER QUESTION]: {query}")
        dummy_file = MockUploadFile(pdf_path)
        answer, source = llm(query=query, files=[dummy_file])
        print(f"[SOURCE]: {source}")
        print(f"[BOT ANSWER]:\n{answer}")
        print("-" * 50)

    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    main()
