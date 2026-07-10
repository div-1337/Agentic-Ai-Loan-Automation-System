# rag/rag_engine.py
# Simplified RAG using basic similarity - no ChromaDB needed

from rag.knowledge_base import KNOWLEDGE_DOCUMENTS

class RAGEngine:
    """
    Simple keyword-based RAG engine.
    No ChromaDB, no vector DB - just works.
    """

    def __init__(self):
        self._initialized = True

    def initialize(self):
        pass  # Nothing to initialize

    def query(self, question: str, n_results: int = 3) -> str:
        """Find relevant docs using keyword matching"""
        question_lower = question.lower()
        
        scored = []
        for doc in KNOWLEDGE_DOCUMENTS:
            text = doc["text"].lower()
            # Score by keyword overlap
            words = set(question_lower.split())
            matches = sum(1 for word in words if word in text and len(word) > 3)
            if matches > 0:
                scored.append((matches, doc["text"]))
        
        # Sort by relevance score
        scored.sort(reverse=True)
        top_docs = [text for _, text in scored[:n_results]]
        
        if not top_docs:
            # Return general product info as fallback
            return KNOWLEDGE_DOCUMENTS[0]["text"]
        
        return "\n\n---\n".join(top_docs)

    def get_objection_response(self, objection_type: str) -> str:
        """Get objection handling context"""
        return self.query(f"handle objection about {objection_type}", n_results=2)

# Singleton
rag_engine = RAGEngine()
