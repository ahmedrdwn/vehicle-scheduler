from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import os
from logic import solve_schedule

app = FastAPI()

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
# We assume the static files are in a 'static' directory next to this file
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(static_dir, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
