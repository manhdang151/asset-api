from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from service.asset_service import AssetService

router = APIRouter()

# --- Request models ---
class CreateAssetBody(BaseModel):
    name: str
    type: str
    status: Optional[str] = "active"

class BatchCreateBody(BaseModel):
    assets: list[CreateAssetBody]

# Biến global - sẽ được gán trong main.py
_service: AssetService = None

def set_service(service: AssetService):
    global _service
    _service = service

# ========== Bài 1: Statistics ==========
@router.get("/assets/stats")
def get_stats():
    return _service.get_stats()

@router.get("/assets/count")
def count_assets(type: Optional[str] = None, status: Optional[str] = None):
    return _service.count_assets(type, status)

# ========== Bài 7: Search (phải đặt TRƯỚC /assets/{id}) ==========
@router.get("/assets/search")
def search_assets(q: str = Query(..., description="Search query")):
    try:
        results = _service.search_by_name(q)
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ========== Bài 6: List + Pagination ==========
@router.get("/assets")
def list_assets(
    page: int = 1,
    limit: int = 20,
    type: Optional[str] = None,
    status: Optional[str] = None,
):
    return _service.list_assets(page, limit, type, status)

# ========== Bài 4: Create đơn lẻ ==========
@router.post("/assets", status_code=201)
def create_asset(body: CreateAssetBody):
    try:
        asset = _service.create_asset(body.name, body.type, body.status)
        return asset
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/assets/{asset_id}")
def get_asset(asset_id: str):
    asset = _service.get_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="asset not found")
    return asset

# ========== Bài 2: Batch Create ==========
@router.post("/assets/batch", status_code=201)
def batch_create(body: BatchCreateBody):
    try:
        inputs = [a.model_dump() for a in body.assets]
        return _service.batch_create(inputs)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ========== Bài 3: Batch Delete ==========
@router.delete("/assets/batch")
def batch_delete(ids: str = Query(..., description="Comma-separated IDs")):
    id_list = [i.strip() for i in ids.split(",") if i.strip()]
    if not id_list:
        raise HTTPException(status_code=400, detail="ids parameter required")
    return _service.batch_delete(id_list)