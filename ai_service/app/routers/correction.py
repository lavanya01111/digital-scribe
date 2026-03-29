from fastapi import APIRouter

router = APIRouter()

@router.post("/correction")
async def process_correction():
    return {"status": "not implemented yet"}
