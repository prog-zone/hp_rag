from typing import List
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_core.prompts import ChatPromptTemplate
from qdrant_client import models as qdrant_models
from app.core.qdrant import qdrant_client
from app.core.config import settings
from app.schemas.retrieval import SearchIntent

class VectorService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        self.vector_store = QdrantVectorStore(
            client=qdrant_client,
            collection_name="harry_potter_collection",
            embedding=self.embeddings,
        )

        self.cross_encoder_model = HuggingFaceCrossEncoder(
            model_name="BAAI/bge-reranker-base"
        )
        
        self.reranker = CrossEncoderReranker(
            model=self.cross_encoder_model, 
            top_n=5
        )

        # NEW: We add a Prompt Template to guide the extraction and rewriting
        system_prompt = """You are an expert Harry Potter search assistant. 
        Analyze the user's query, extract any specific book titles mentioned, and rewrite the query to be highly optimized for a semantic vector database search."""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{question}")
        ])

        # Chain the prompt into the LLM with structured output
        self.intent_extractor = prompt | ChatOpenAI(
            model="gpt-4o-mini", 
            temperature=0, 
            openai_api_key=settings.OPENAI_API_KEY
        ).with_structured_output(SearchIntent)

    async def query(self, question: str, initial_limit: int = 30) -> List[Document]:
        # STEP 1: Extract Intent & Rewrite Query (One single LLM call!)
        intent: SearchIntent = await self.intent_extractor.ainvoke({"question": question})
        
        optimized_query = intent.optimized_query
        print(f"Original: {question}")
        print(f"Optimized: {optimized_query}")
        
        # STEP 2: Build the Qdrant Filter 
        qdrant_filter = None
        if intent.book_titles and len(intent.book_titles) > 0:
            print(f"Applying Filter for: {intent.book_titles}")
            
            book_conditions = [
                qdrant_models.FieldCondition(
                    key="metadata.book_title",
                    match=qdrant_models.MatchValue(value=title),
                )
                for title in intent.book_titles
            ]
            qdrant_filter = qdrant_models.Filter(should=book_conditions)

        # STEP 3: Broad Dense Retrieval (Using the OPTIMIZED query)
        results_with_scores = await self.vector_store.asimilarity_search_with_score(
            query=optimized_query, # Changed from 'question'
            k=initial_limit,
            filter=qdrant_filter 
        )

        # STEP 4: Filtering out 'noise'
        relevant_docs = []
        for doc, score in results_with_scores:
            if score > 0.30: 
                doc.metadata["dense_score"] = score 
                relevant_docs.append(doc)
        
        if not relevant_docs:
            return []

        # STEP 5: Reranking (Using the OPTIMIZED query)
        reranked_docs = self.reranker.compress_documents(
            documents=relevant_docs, 
            query=optimized_query
        )
        
        return reranked_docs