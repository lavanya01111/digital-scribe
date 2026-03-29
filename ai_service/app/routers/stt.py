from fastapi import APIRouter

router = APIRouter()

@router.post("/stt")
async def process_stt():
    return {"status": "not implemented yet"}
