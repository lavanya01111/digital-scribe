from fastapi import APIRouter

router = APIRouter()

@router.post("/tts")
async def process_tts():
    return {"status": "not implemented yet"}
