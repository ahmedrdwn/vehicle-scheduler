from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import sys
import traceback

# Import logic with error handling
try:
    from logic import solve_schedule
except ImportError as e:
    # Fallback for debugging
    print(f"Import error: {e}", file=sys.stderr)
    solve_schedule = None

app = FastAPI(title="Vehicle Scheduler API")

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

@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return JSONResponse(content={
        "status": "ok",
        "logic_imported": solve_schedule is not None,
        "python_version": sys.version
    })

@app.post("/api/solve")
async def solve(request: SolveRequest):
    try:
        if solve_schedule is None:
            raise HTTPException(status_code=500, detail="Logic module not imported")
        # Convert Pydantic models to dicts for the logic function
        trips_data = [t.dict() for t in request.trips]
        result = solve_schedule(trips_data, request.dh_matrix)
        return result
    except HTTPException:
        raise
    except Exception as e:
        error_details = {
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }
        print(f"Error in solve: {error_details}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))

# Serve static files - handle multiple path scenarios for Vercel
def get_static_path():
    """Get the path to static files, trying multiple locations"""
    base_dir = os.path.dirname(__file__)
    possible_paths = [
        os.path.join(base_dir, "static", "index.html"),
        os.path.join(os.getcwd(), "web_app", "static", "index.html"),
        os.path.join(os.getcwd(), "static", "index.html"),
        "web_app/static/index.html",
        "static/index.html"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

@app.get("/", response_class=HTMLResponse)
async def read_index():
    index_path = get_static_path()
    try:
        if index_path and os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        else:
            # Fallback HTML with basic structure
            return HTMLResponse(
                content="""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Vehicle Scheduler</title>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <script src="https://cdn.tailwindcss.com"></script>
                    <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
                </head>
                <body class="bg-gray-50 p-8">
                    <h1 class="text-2xl font-bold mb-4">Vehicle Scheduler</h1>
                    <p class="text-gray-600">Static files not found. Please check deployment configuration.</p>
                    <p class="text-sm text-gray-500 mt-2">Path attempted: {}</p>
                </body>
                </html>
                """.format(index_path or "None"),
                status_code=200
            )
    except Exception as e:
        return HTMLResponse(
            content=f"<h1>Error loading page</h1><p>{str(e)}</p><p>Path: {index_path}</p>",
            status_code=500
        )

# Export app for Vercel (required for serverless functions)
# Vercel's Python runtime looks for 'handler' or 'app'
handler = app
__all__ = ['handler', 'app']
