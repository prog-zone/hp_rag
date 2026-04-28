from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_documents(documents):
    # 600-800 tokens is the sweet spot for context vs precision.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100, # 15% overlap prevents cutting context in half
        add_start_index=True, # Stores the character position for citations
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f" Split into {len(chunks)} total chunks.")
    return chunks