import time
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from app.services.vector_service import VectorService
from app.core.config import settings

class RAGService:
    def __init__(self):
        self.vector_service = VectorService()
        self.llm = ChatOpenAI(
            model="gpt-5.4-mini", # Fast, cheap, and smart
            temperature=0,       # Keep it deterministic for RAG
            openai_api_key=settings.OPENAI_API_KEY
        )
        
    def _format_docs(self, docs):
        """
        Formats the retrieved chunks into a clear string for the LLM.
        Includes citations so the LLM knows where each piece came from.
        """
        formatted = []
        for i, doc in enumerate(docs):
            content = f"--- Source {i+1}: {doc.metadata.get('book_title', 'Unknown')} (Page {doc.metadata.get('page', 'Unknown')}) ---\n{doc.page_content}"
            formatted.append(content)
        return "\n\n".join(formatted)

    async def answer_question(self, question: str) -> Dict[str, Any]:
        # Start the stopwatch!
        start_time = time.time()
        
        # 1. Retrieve the relevant chunks
        docs = await self.vector_service.query(question)
        
        # Handle the edge case where no documents meet our 0.30 threshold
        if not docs:
            return {
                "answer": "I'm sorry, I couldn't find any specific information about that in the Harry Potter books.",
                "sources": [],
                "time_taken_seconds": round(time.time() - start_time, 2),
                "chunks_used": 0
            }

        context = self._format_docs(docs)

        # NEW: Build a clean list of sources to return to the user/frontend
        sources_data = []
        for doc in docs:
            sources_data.append({
                "book_title": doc.metadata.get("book_title", "Unknown"),
                "page": doc.metadata.get("page", "Unknown"),
                "dense_score": round(doc.metadata.get("dense_score", 0), 3) # Showing off our threshold score!
            })

        # 2. Define the System Prompt
        template = """You are a highly knowledgeable Harry Potter scholar. 
        Use the following pieces of retrieved context to answer the user's question. 
        
        Rules:
        1. If the answer isn't in the context, say you don't know. Do not use outside knowledge.
        2. Always cite which Book and Page you are referring to within your answer.
        3. Keep the tone academic yet engaging.

        Context:
        {context}

        Question: {question}

        Answer:"""

        prompt = ChatPromptTemplate.from_template(template)

        # 3. The Chain (LCEL)
        chain = (
            {"context": lambda x: context, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

        # Generate the answer
        answer = await chain.ainvoke(question)
        
        # Stop the stopwatch!
        end_time = time.time()

        # 4. Return our rich payload
        return {
            "sources": sources_data,
            "time_taken_seconds": round(end_time - start_time, 2),
            "chunks_used": len(docs),
            "answer": answer,
            "raw_context": context
        }