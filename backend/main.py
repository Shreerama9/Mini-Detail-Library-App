from fastapi import FastAPI, HTTPException, Query, Header, Request  
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional 
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

try:
    from rag_service import rag_suggest_detail, generate_embeddings_for_details
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

load_dotenv()

DATABASE_URL= os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set!")



if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

if "sslmode" not in DATABASE_URL:
    if "localhost" in DATABASE_URL or "127.0.0.1" in DATABASE_URL:
        if "?" in DATABASE_URL:
            DATABASE_URL += "&sslmode=disable"
        else:
            DATABASE_URL += "?sslmode=disable"
    else:
        if "?" in DATABASE_URL:
            DATABASE_URL += "&sslmode=require"
        else:
            DATABASE_URL += "?sslmode=require"


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    )


class Detail(BaseModel):
    id : int
    title : str
    category : str
    tags : List[str]
    description : str

class SuggestRequest(BaseModel):
    host_element : str
    adjacent_element : str
    exposure : str


class SuggestResponse(BaseModel):
    detail : Optional[Detail]
    explanation : str


class DetailWithReason(BaseModel):
    id: int
    title: str
    category: str
    tags: List[str]
    description: str
    reason: str
    rank: int


class SuggestMultiResponse(BaseModel):
    suggestions: List[DetailWithReason]
    summary: str


app = FastAPI(
    title = "Architectural Detail Library",
    description = "API for architectural detail suggestions",
    version = '1.0.0'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)




def row_to_detail(row) -> Detail:
    return Detail(
        id=row[0],
        title=row[1],
        category=row[2],
        tags=row[3],
        description=row[4]
    )


@app.get("/details", response_model=List[Detail])
def list_details():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id,title, category, tags, description
            FROM details
            ORDER BY id
        """
        ))
        details = [row_to_detail(row) for row in result]
    return details


@app.get("/details/search", response_model=List[Detail])
def search_details(q:str = Query(..., min_length=1, description="Search query")):
    search_pattern = f"%{q}%"

    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, title, category, tags, description
            FROM details
            WHERE 
                title ILIKE :pattern
                OR description ILIKE :pattern
                OR :query = ANY(tags)
                OR EXISTS (
                    SELECT 1 FROM unnest(tags) AS tag
                    WHERE tag ILIKE :pattern
                )
            ORDER BY id
        """
        ), 
        {"pattern": search_pattern, "query": q.lower()}
        )
        
        details = [row_to_detail(row) for row in result]

    return details


@app.post("/suggest-detail", response_model=SuggestResponse)
def suggest_detail(request: SuggestRequest):
    with engine.connect() as conn:
        result = conn.execute(text("""
        SELECT d.id, d.title, d.category, d.tags, d.description
        FROM detail_usage_rules r
        JOIN details d ON r.detail_id = d.id
        WHERE 
            LOWER(r.host_element) = LOWER(:host)
            AND LOWER(r.adjacent_element) = LOWER(:adjacent)
            AND LOWER(r.exposure) = LOWER(:exposure)
        LIMIT 1
"""

    ),{
        "host" : request.host_element,
        "adjacent" : request.adjacent_element,
        "exposure" : request.exposure
    })
    row = result.fetchone()


    if row:
        detail = row_to_detail(row)
        explanation = (
            f"Based on your context:\n"
            f"• Host Element: {request.host_element}\n"
            f"• Adjacent Element: {request.adjacent_element}\n"
            f"• Exposure: {request.exposure}\n\n"
            f"We recommend '{detail.title}' because it specifically addresses "
            f"the junction between {request.host_element.lower()} and "
            f"{request.adjacent_element.lower()} in {request.exposure.lower()} conditions. "
            f"This detail covers: {detail.description.lower()}"
        )
        return SuggestResponse(detail=detail, explanation=explanation)
    else:
        explanation = (
            f"No matching detail found for:\n"
            f"• Host Element: {request.host_element}\n"
            f"• Adjacent Element: {request.adjacent_element}\n"
            f"• Exposure: {request.exposure}\n\n"
            f"Try different combinations. Available contexts include:\n"
            f"• External Wall + Slab + External\n"
            f"• Window + External Wall + External\n"
            f"• Internal Wall + Floor + Internal"
        )
        return SuggestResponse(detail=None, explanation=explanation)


@app.get("/")
def root():
    return {
        "message": "Architectural Detail Library API",
        "docs": "/docs",
        "endpoints": [
            "GET /details - List all details",
            "GET /details/search?q=<query> - Search details",
            "POST /suggest-detail - Get detail suggestion"
        ]
    }


@app.post("/suggest-detail-rag", response_model=SuggestMultiResponse)
def suggest_detail_rag(request : SuggestRequest):
    if not RAG_AVAILABLE:
        raise HTTPException(status_code=503, detail = "RAG Service not available")
    
    suggestions, summary = rag_suggest_detail(
        engine,
        request.host_element,
        request.adjacent_element,
        request.exposure,
        top_n=2
    )

    if suggestions:
        return SuggestMultiResponse(
            suggestions= [DetailWithReason(**s) for s in suggestions],
            summary = summary
        )
    else:
        return SuggestMultiResponse(suggestions=[], summary=summary)
    

@app.post("/generate-embeddings")
def generate_embeddings():
    if not RAG_AVAILABLE:
        raise HTTPException(status_code=503, detail="RAG service not available")
    
    count = generate_embeddings_for_details(engine)
    return {"message":f"Generated embeddings for {count} details"}


@app.get("/security/details", response_model=List[Detail])
def get_secure_details(
    x_user_email: str = Header(None),
    x_user_role: str = Header(None)
):
    if not x_user_role:
        raise HTTPException(
            status_code = 401,
            detail="Missing X-USER-ROLE header"
        )

    role = x_user_role.lower()

    if role not in ["admin", "architect"]:
        raise HTTPException(
            status_code=403,
            detail=f"Invalid role '{role}'. Must be 'admin' or 'architect'"
        )

    with engine.connect() as conn:
        trans = conn.begin()
        try:
            conn.execute(text(f"SET LOCAL app.current_user_role = '{role}'"))

            result = conn.execute(text("""
                SELECT id, title, category, tags, description
                FROM details
                ORDER BY id
            """))

            details = [row_to_detail(row) for row in result]
            trans.commit()
        except Exception as e:
            trans.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return details


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",            
        host="0.0.0.0",        
        port=8000,             
        reload=True
    )   