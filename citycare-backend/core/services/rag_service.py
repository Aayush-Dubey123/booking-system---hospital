import math
from datetime import datetime
from typing import Optional
from core.database.database import MongoDatabase
from common.embedding_service import get_embedding
from common.logger import logger

logging = logger(__name__)


def _cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


class RAGService:
    def __init__(self) -> None:
        self.db = MongoDatabase()
        self.collection = self.db["prescription_vectors"]

    async def index_prescription(
        self,
        prescription_id: str,
        appointment_id: str,
        patient_id: str,
        doctor_id: str,
        patient_name: str,
        doctor_name: str,
        diagnosis: str,
        medicines: str,
        notes: str = "",
        created_at: Optional[datetime] = None,
    ) -> dict:
        """
        Construct chunk text, generate vector embedding via Ollama, and store in MongoDB.
        Avoids duplicate indexing if prescription_id is already indexed.
        """
        try:
            logging.info(f"Indexing prescription {prescription_id} for RAG")

            # De-duplication check
            existing = await self.collection.find_one({"prescription_id": prescription_id})
            if existing:
                logging.info(f"Prescription {prescription_id} is already indexed. Skipping.")
                return existing

            chunk_text = (
                f"Prescription Summary:\n"
                f"Prescription ID: {prescription_id}\n"
                f"Patient Name: {patient_name}\n"
                f"Doctor Name: {doctor_name}\n"
                f"Diagnosis: {diagnosis}\n"
                f"Prescribed Medicines & Dosage: {medicines}\n"
                f"Special Notes/Instructions: {notes or 'None'}\n"
            )

            # Generate dynamic embedding from Ollama model
            embedding = await get_embedding(chunk_text)

            doc = {
                "prescription_id": prescription_id,
                "appointment_id": appointment_id,
                "patient_id": patient_id,
                "doctor_id": doctor_id,
                "text": chunk_text,
                "embedding": embedding,
                "created_at": created_at or datetime.utcnow(),
            }

            result = await self.collection.insert_one(doc)
            doc["_id"] = result.inserted_id
            logging.info(
                f"Successfully indexed prescription {prescription_id} into prescription_vectors"
            )
            return doc
        except Exception as error:
            logging.error(f"Error indexing prescription {prescription_id}: {error}")
            raise

    async def search_prescriptions(
        self,
        patient_id: str,
        query: str,
        top_k: int = 3,
        similarity_threshold: float = 0.4,
    ) -> list[dict]:
        """
        Search prescription vectors strictly scoped to patient_id.
        Applies similarity_threshold filtering (default 0.4) and top_k limit (default 3).
        Tries Atlas $vectorSearch first, falls back to similarity calculation over documents strictly matching patient_id.
        """
        try:
            logging.info(f"RAG search for patient_id: {patient_id}, query: '{query}', top_k: {top_k}, threshold: {similarity_threshold}")
            if not query or not query.strip():
                return []

            query_vector = await get_embedding(query)

            # 1. Try Atlas $vectorSearch with patient_id filter
            try:
                pipeline = [
                    {
                        "$vectorSearch": {
                            "index": "vector_index",
                            "path": "embedding",
                            "queryVector": query_vector,
                            "numCandidates": top_k * 10,
                            "limit": top_k,
                            "filter": {"patient_id": patient_id},
                        }
                    },
                    {
                        "$project": {
                            "prescription_id": 1,
                            "patient_id": 1,
                            "text": 1,
                            "score": {"$meta": "vectorSearchScore"},
                        }
                    },
                ]
                cursor = self.collection.aggregate(pipeline)
                raw_results = await cursor.to_list(length=top_k)
                filtered = [r for r in raw_results if r.get("score", 1.0) >= similarity_threshold]
                if filtered:
                    logging.info(f"Atlas $vectorSearch returned {len(filtered)} matches above threshold {similarity_threshold}")
                    return filtered
            except Exception as search_err:
                logging.info(
                    f"Atlas $vectorSearch unavailable ({search_err}). Falling back to similarity search."
                )

            # 2. Fallback: Filter MongoDB documents strictly by patient_id, compute cosine similarity
            cursor = self.collection.find({"patient_id": patient_id})
            user_docs = await cursor.to_list(length=100)

            if not user_docs:
                logging.info(f"No prescription vectors found for patient_id: {patient_id}")
                return []

            scored_docs = []
            for doc in user_docs:
                doc_vec = doc.get("embedding")
                if doc_vec and isinstance(doc_vec, list):
                    sim = _cosine_similarity(query_vector, doc_vec)
                    if sim >= similarity_threshold:
                        scored_docs.append({
                            "prescription_id": doc.get("prescription_id"),
                            "patient_id": doc.get("patient_id"),
                            "text": doc.get("text"),
                            "score": sim,
                        })

            scored_docs.sort(key=lambda x: x["score"], reverse=True)
            top_results = scored_docs[:top_k]
            logging.info(
                f"Fallback similarity search returned {len(top_results)} matches above threshold {similarity_threshold} for patient_id: {patient_id}"
            )
            return top_results

        except Exception as error:
            logging.error(f"Error in RAG search for patient {patient_id}: {error}")
            raise
