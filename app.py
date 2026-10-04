from pathlib import Path
import traceback
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from backend import run_travel_agent

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="AI Travel Planning System",
    description="LangGraph Multi-agent Travel Planner with FastAPI Frontend",
    version="1.0.0"
)

# Static files mounting
app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
)

# Template engine configuration
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


class TravelRequest(BaseModel):
    message: str
    thread_id: str | None = None


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request}
    )
@app.post("/api/travel")
async def travel_planner(request_data: TravelRequest):
    try:
        user_message = request_data.message.strip()

        if not user_message:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "Message cannot be empty"
                }
            )

        print("=" * 60)
        print("USER REQUEST:", user_message)
        print("THREAD ID:", request_data.thread_id)
        print("Calling travel agent...")
        print("=" * 60)

        result = await run_in_threadpool(
            run_travel_agent,
            user_input=user_message,
            thread_id=request_data.thread_id
        )

        print("=" * 60)
        print("TRAVEL AGENT COMPLETED")
        print("RESULT:", result)
        print("=" * 60)

        return JSONResponse(
            content={
                "success": True,
                "thread_id": result.get("thread_id"),
                "answer": result.get("answer"),
                "flight_results": result.get("flight_results"),
                "hotel_results": result.get("hotel_results"),
                "itinerary": result.get("itinerary"),
                "llm_calls": result.get("llm_calls")
            }
        )

    except Exception as e:
        print("=" * 60)
        print("TRAVEL AGENT ERROR")
        print(str(e))
        traceback.print_exc()
        print("=" * 60)

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "message": "AI travel planner API is running"
    }


@app.get("/favicon.ico")
async def favicon():
    return JSONResponse(content={})


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )