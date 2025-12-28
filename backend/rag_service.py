import os
os.environ['SENTENCE_TRANSFORMERS_HOME'] = '/tmp/sentence_transformers'



from typing import List, Optional, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
import google.generativeai as genai
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

EMBEDDING_MODEL = None
RERANKER_MODEL = None
GEMINI_MODEL = None

def get_embedding_model():
    global EMBEDDING_MODEL
    if EMBEDDING_MODEL is None:
        EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
    return EMBEDDING_MODEL

def get_reranker_model():
    global RERANKER_MODEL
    if RERANKER_MODEL is None:
        RERANKER_MODEL = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    return RERANKER_MODEL

def get_gemini_model():
    global GEMINI_MODEL
    if GEMINI_MODEL is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            GEMINI_MODEL = genai.GenerativeModel('gemini-1.5-flash')
    return GEMINI_MODEL


def generate_embedding(text: str) -> List[float]:

    model = get_embedding_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def generate_embeddings_for_details(engine) -> int:

    model = get_embedding_model()
    updated = 0
    
    with engine.connect() as conn:

        result = conn.execute(text("""
            SELECT id, title, description, tags 
            FROM details 
            WHERE embedding IS NULL
        """))
        rows = result.fetchall()
        
        for row in rows:
            combined_text = f"{row[1]} {row[2]} {' '.join(row[3])}"
            embedding = model.encode(combined_text, convert_to_numpy=True)
            
            conn.execute(text("""
                UPDATE details 
                SET embedding = :embedding 
                WHERE id = :id
            """), {"embedding": embedding.tolist(), "id": row[0]})
            updated += 1
        
        conn.commit()
    
    return updated


def vector_search(engine, query: str, top_k: int = 20) -> List[dict]:

    query_embedding = generate_embedding(query)
    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
    
    with engine.connect() as conn:
        result = conn.execute(text(f"""
            SELECT 
                id, title, category, tags, description,
                1 - (embedding <=> '{embedding_str}'::vector) as similarity
            FROM details 
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> '{embedding_str}'::vector
            LIMIT :top_k
        """), {"top_k": top_k})
        
        details = []
        for row in result:
            details.append({
                "id": row[0],
                "title": row[1],
                "category": row[2],
                "tags": row[3],
                "description": row[4],
                "similarity": float(row[5])
            })
        
    return details


def rerank_results(query: str, candidates: List[dict], top_k: int = 3) -> List[dict]:
    if not candidates:
        return []
    
    reranker = get_reranker_model()
    
    pairs = [(query, f"{d['title']} {d['description']}") for d in candidates]
    
    scores = reranker.predict(pairs)
    for i, candidate in enumerate(candidates):
        candidate["rerank_score"] = float(scores[i])
    reranked = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)
    
    return reranked[:top_k]


def generate_explanation_with_ai(
    query_context: str,
    matched_detail: dict,
    host_element: str,
    adjacent_element: str,
    exposure: str
) -> str:
    """
    Generate intelligent explanation using Google Gemini.
    Falls back to template if API unavailable.
    """
    gemini = get_gemini_model()
    
    if gemini is None:
        return (
            f"Based on your context:\n"
            f"• Host Element: {host_element}\n"
            f"• Adjacent Element: {adjacent_element}\n"
            f"• Exposure: {exposure}\n\n"
            f"We recommend '{matched_detail['title']}' because it addresses "
            f"the junction between {host_element.lower()} and "
            f"{adjacent_element.lower()} in {exposure.lower()} conditions."
        )
    
    try:
        prompt = f"""You are an architectural detail expert. Based on the following context, explain why this detail is recommended.

User Context:
- Host Element: {host_element}
- Adjacent Element: {adjacent_element}
- Exposure: {exposure}

Recommended Detail:
- Title: {matched_detail['title']}
- Category: {matched_detail['category']}
- Description: {matched_detail['description']}
- Tags: {', '.join(matched_detail['tags'])}

Provide a clear, professional explanation (2-3 sentences) of why this detail is the best match for the user's requirements. Focus on technical relevance and practical application."""

        response = gemini.generate_content(prompt)
        return response.text.strip()
    
    except Exception as e:
        return (
            f"Recommended: '{matched_detail['title']}'\n\n"
            f"This detail is suitable for {host_element} meeting {adjacent_element} "
            f"in {exposure} conditions. {matched_detail['description']}"
        )


def rag_suggest_detail(
    engine,
    host_element: str,
    adjacent_element: str,
    exposure: str,
    top_n: int = 2
) -> Tuple[Optional[List[dict]], str]:
    """
    RAG pipeline for detail suggestion:
    1. Create query from context
    2. Vector search for candidates
    3. Rerank for best matches
    4. Generate AI explanation for each
    
    Returns (list of details with reasons, summary) tuple.
    """
    query = f"{host_element} {adjacent_element} junction detail {exposure} conditions"
    candidates = vector_search(engine, query, top_k=20)
    
    if not candidates:
        return None, (
            f"No matching details found for:\n"
            f"• Host Element: {host_element}\n"
            f"• Adjacent Element: {adjacent_element}\n"
            f"• Exposure: {exposure}\n\n"
            f"The database may need to be populated with more architectural details."
        )
    
    # Step 2: Rerank - get top N
    reranked = rerank_results(query, candidates, top_k=top_n)
    
    # Step 3: Format each suggestion with reason
    suggestions = []
    for i, match in enumerate(reranked[:top_n]):
        reason = generate_explanation_with_ai(
            query,
            match,
            host_element,
            adjacent_element,
            exposure
        )
        suggestions.append({
            "id": match["id"],
            "title": match["title"],
            "category": match["category"],
            "tags": match["tags"],
            "description": match["description"],
            "reason": reason,
            "rank": i + 1
        })
    
    summary = f"Found {len(suggestions)} relevant details for {host_element} + {adjacent_element} ({exposure})"
    
    return suggestions, summary

