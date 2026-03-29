# ai_service/app/routers/handwriting.py
# Handles the /api/handwriting POST endpoint.
# Input: base64 PNG image from Canvas API
# Output: recognized text string

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import base64, io
from PIL import Image
from app.models.htr_model import recognize_handwriting

router = APIRouter()

# Request body schema — base64 image string
class HandwritingRequest(BaseModel):
    image_base64: str   # PNG image encoded as base64

@router.post("/handwriting")
async def handwriting_recognition(req: HandwritingRequest):
    try:
        # Decode base64 string back to image bytes
        image_bytes = base64.b64decode(req.image_base64)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        # Pass to our HTR model for inference
        raw_text = recognize_handwriting(image)
        return {"raw_text": raw_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
