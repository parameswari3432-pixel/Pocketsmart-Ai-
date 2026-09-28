import os
import logging
from typing import Optional
from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from gemini_utils import (
    generate_interior_plan,
    generate_party_plan,
    generate_jewelry_plan,
    GEMINI_API_KEY
)

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pocketsmart")

app = FastAPI(
    title="PocketSmart AI",
    description="Intelligent Budget & Lifestyle Planners powered by Gemini AI",
    version="1.0.0"
)

# Ensure folders exist
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# Mount static files and templates
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# --- Pydantic Request Models ---
class InteriorRequest(BaseModel):
    budget: float = Field(..., gt=0, description="Total budget amount")
    room_type: str = Field(..., description="Living Room, Bedroom, Kitchen, etc.")
    style: str = Field("Modern Minimalist", description="Aesthetic style")
    square_feet: float = Field(250.0, gt=0, description="Room area in square feet")
    priorities: str = Field("balanced", description="Focus area or priority")
    currency: str = Field("$", description="Currency symbol")


class PartyRequest(BaseModel):
    budget: float = Field(..., gt=0, description="Total party budget")
    event_type: str = Field("Birthday Party", description="Type of event")
    guest_count: int = Field(20, gt=0, description="Number of expected guests")
    theme: str = Field("Boho Chic", description="Theme or vibe")
    venue_type: str = Field("Home / Backyard", description="Location type")
    currency: str = Field("$", description="Currency symbol")


# --- HTML Page Routes ---
@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """Render the main PocketSmart AI landing hub & dashboard."""
    has_api_key = bool(GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here")
    return templates.TemplateResponse(
    request=request,
    name="index.html",
    context={
        "request": request,
        "active_tab": "home",
        "has_api_key": has_api_key
        }
    )


@app.get("/interior", response_class=HTMLResponse)
async def interior_page(request: Request):
    """Render Home Interior Budget Planner UI."""
    return templates.TemplateResponse(
    request=request,
    name="interior.html",
    context={
        "request": request,
        "active_tab": "interior"
    }
)   


@app.get("/party", response_class=HTMLResponse)
async def party_page(request: Request):
    """Render Party Budget Planner UI."""
    return templates.TemplateResponse(
       request=request,
       name="party.html",
       context={
        "request": request,
        "active_tab": "party"
    }
)
    


@app.get("/jewelry", response_class=HTMLResponse)
async def jewelry_page(request: Request):
    """Render Jewelry & Outfit Budget Planner UI."""
    return templates.TemplateResponse(
       request=request,
       name="jewelry.html",
       context={
          "request": request,
          "active_tab": "party"
       }
    )    


# --- API Generation Endpoints ---
@app.post("/api/interior/generate")
async def api_generate_interior(payload: InteriorRequest):
    """Generate budget & styling plan for home interiors."""
    try:
        plan = generate_interior_plan(
            budget=payload.budget,
            room_type=payload.room_type,
            style=payload.style,
            square_feet=payload.square_feet,
            priorities=payload.priorities,
            currency=payload.currency
        )
        return JSONResponse(content={"success": True, "plan": plan})
    except Exception as e:
        logger.error(f"Error in api_generate_interior: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/party/generate")
async def api_generate_party(payload: PartyRequest):
    """Generate event planning budget and timeline."""
    try:
        plan = generate_party_plan(
            budget=payload.budget,
            event_type=payload.event_type,
            guest_count=payload.guest_count,
            theme=payload.theme,
            venue_type=payload.venue_type,
            currency=payload.currency
        )
        return JSONResponse(content={"success": True, "plan": plan})
    except Exception as e:
        logger.error(f"Error in api_generate_party: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/jewelry/generate")
async def api_generate_jewelry(
    budget: float = Form(...),
    occasion: str = Form("Wedding Guest"),
    style_preference: str = Form("Contemporary Minimalist"),
    metals: str = Form("Yellow Gold / Lab Diamond"),
    currency: str = Form("$"),
    outfit_image: Optional[UploadFile] = File(None)
):
    """Generate jewelry budget plan with optional outfit image multimodal matching."""
    try:
        image_bytes = None
        image_mime = None

        if outfit_image and outfit_image.filename:
            image_bytes = await outfit_image.read()
            image_mime = outfit_image.content_type or "image/jpeg"

        plan = generate_jewelry_plan(
            budget=budget,
            occasion=occasion,
            style_preference=style_preference,
            metals=metals,
            outfit_image_bytes=image_bytes,
            outfit_image_mime=image_mime,
            currency=currency
        )
        return JSONResponse(content={"success": True, "plan": plan})
    except Exception as e:
        logger.error(f"Error in api_generate_jewelry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": "PocketSmart AI",
        "gemini_configured": bool(GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here")
    }


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=True)
