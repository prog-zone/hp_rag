import os
from langchain_community.document_loaders import PyMuPDFLoader

BOOK_TITLES = {
    "harrypotter_1.pdf": "Harry Potter and the Sorcerer's Stone",
    "harrypotter_2.pdf": "Harry Potter and the Chamber of Secrets",
    "harrypotter_3.pdf": "Harry Potter and the Prisoner of Azkaban",
    "harrypotter_4.pdf": "Harry Potter and the Goblet of Fire",
    "harrypotter_5.pdf": "Harry Potter and the Order of the Phoenix",
    "harrypotter_6.pdf": "Harry Potter and the Half-Blood Prince",
    "harrypotter_7.pdf": "Harry Potter and the Deathly Hallows",
}

def load_hp_docs(data_path: str):
    all_documents = []
    
    for filename in os.listdir(data_path):
        if filename.endswith(".pdf") and filename in BOOK_TITLES:
            file_path = os.path.join(data_path, filename)
            loader = PyMuPDFLoader(file_path)
            
            docs = loader.load()
            for doc in docs:
                doc.metadata["book_title"] = BOOK_TITLES[filename]
                doc.metadata["source"] = filename
            
            all_documents.extend(docs)
            print(f"Loaded {filename}: {len(docs)} pages")
            
    return all_documents