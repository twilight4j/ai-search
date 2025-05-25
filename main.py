from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(
    title="AI Search API",
    description="AI-powered product search API for e-commerce platform",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchQuery(BaseModel):
    query: str
    limit: Optional[int] = 10

class ProductResponse(BaseModel):
    product_id: str
    name: str
    description: str
    price: float
    category: str
    similarity_score: float

@app.get("/")
async def root():
    return {"message": "AI Search API is running"}

@app.post("/search", response_model=List[ProductResponse])
async def search_products(query: SearchQuery):
    try:
        # TODO: Implement search logic using Langchain and FAISS
        # This is a placeholder response
        return [
            ProductResponse(
                product_id="sample_id",
                name="Sample Product",
                description="Sample description",
                price=100000.0,
                category="Electronics",
                similarity_score=0.95
            )
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 