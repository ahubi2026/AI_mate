# rag.py — ChromaDB RAG 검색 모듈
# ============================================================
# logic.py의 get_ai_reply()에서 호출하여
# 사용자 질문과 관련된 코칭 지식을 검색합니다.
# ============================================================

import os
import chromadb
from chromadb.utils import embedding_functions

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_db")

# 전역 캐시 (매번 로드 방지)
_client     = None
_collection = None
_ef         = None


def _get_embedding_fn():
    global _ef
    if _ef is not None:
        return _ef
    try:
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="jhgan/ko-sroberta-multitask"
        )
        ef(["테스트"])
        _ef = ef
    except Exception:
        try:
            ef = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="paraphrase-multilingual-MiniLM-L12-v2"
            )
            ef(["테스트"])
            _ef = ef
        except Exception:
            _ef = embedding_functions.DefaultEmbeddingFunction()
    return _ef


def get_collection():
    """ChromaDB 컬렉션 반환 (싱글톤)"""
    global _client, _collection
    if _collection is not None:
        return _collection
    if not os.path.exists(DB_DIR):
        return None
    try:
        _client     = chromadb.PersistentClient(path=DB_DIR)
        _collection = _client.get_collection(
            name="coaching_kb",
            embedding_function=_get_embedding_fn()
        )
        return _collection
    except Exception as e:
        print(f"[RAG] 컬렉션 로드 실패: {e}")
        return None


def search(query: str, factor: str, n_results: int = 3) -> str:
    """
    사용자 메시지 + 취약 요인으로 관련 코칭 지식 검색

    Args:
        query:    사용자 메시지
        factor:   취약 요인 키 ("behavior" / "natural" / "thought")
        n_results: 검색 결과 수

    Returns:
        검색된 지식 텍스트 (없으면 빈 문자열)
    """
    collection = get_collection()
    if collection is None:
        return ""

    try:
        # 해당 요인의 문서만 검색
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where={"factor": factor}
        )
        docs = results["documents"][0]
        if not docs:
            return ""
        return "\n\n".join(f"• {doc}" for doc in docs)

    except Exception as e:
        print(f"[RAG] 검색 오류: {e}")
        return ""


def search_rolemodel(role_model_name: str) -> str:
    """롤모델 이름으로 해당 철학 검색"""
    collection = get_collection()
    if collection is None:
        return ""
    try:
        results = collection.query(
            query_texts=[role_model_name],
            n_results=1,
            where={"category": "role_model"}
        )
        docs = results["documents"][0]
        return docs[0] if docs else ""
    except Exception:
        return ""


def is_ready() -> bool:
    """RAG 사용 가능 여부 확인"""
    return get_collection() is not None
