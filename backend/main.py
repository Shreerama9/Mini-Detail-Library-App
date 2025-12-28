from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional 
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os


load_dotenv()

DATABASE_URL= os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set!")


# DB connection
engine = create_engine(DATABASE_URL)

# Pydantic Model
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
    detail : Optional
    explanation : str




# Developing FastAPI app
app = FastAPI(
    title = "PiAxis mini detail library",
    description = "API for architectural detail suggestions",
    version = '1.0.0'
)



# CORS Middleware
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


# ENDPOINT1 : GET/details
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

# ENDPOINT2 : GET /details/search
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




#ENDPOINT3
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
    

# ENDPOINT4
@app.get("/")
def root():
    return {
        "message": "PiAxis Mini Detail Library API",
        "docs": "/docs",
        "endpoints": [
            "GET /details - List all details",
            "GET /details/search?q=<query> - Search details",
            "POST /suggest-detail - Get detail suggestion"
        ]
    }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",            
        host="0.0.0.0",        
        port=8000,             
        reload=True
    )   