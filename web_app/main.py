from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import os
from logic import solve_schedule

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class Trip(BaseModel):
    id: int
    dep_term: str
    dep_time: int # Minutes from midnight
    arr_term: str
    arr_time: int # Minutes from midnight

class SolveRequest(BaseModel):
    trips: List[Trip]
    dh_matrix: Dict[str, Dict[str, int]]

@app.post("/api/solve")
async def solve(request: SolveRequest):
    try:
        # Convert Pydantic models to dicts for the logic function
        trips_data = [t.dict() for t in request.trips]
        result = solve_schedule(trips_data, request.dh_matrix)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve static files
static_dir = os.path.join(os.path.dirname(__file__), "static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    index_path = os.path.join(static_dir, "index.html")
    try:
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        else:
            # Fallback if file not found
            return HTMLResponse(content="<h1>Application Error: Static files not found</h1>", status_code=404)
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error loading page: {str(e)}</h1>", status_code=500)

# Export app for Vercel (required for serverless functions)
handler = app
