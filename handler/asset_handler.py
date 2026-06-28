from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from service.asset_service import AssetService
import socket
import ssl
import whois
import uuid

router = APIRouter()

class CreateAssetBody(BaseModel):
    name: str
    type: str
    status: Optional[str] = "active"

class BatchCreateBody(BaseModel):
    assets: list[CreateAssetBody]

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

# ========== Bài 7: Search ==========
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

# ========== Bài 4: Create ==========
@router.post("/assets", status_code=201)
def create_asset(body: CreateAssetBody):
    try:
        asset = _service.create_asset(body.name, body.type, body.status)
        return asset
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

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
    valid_ids = []
    invalid_count = 0
    for i in id_list:
        try:
            uuid.UUID(i)
            valid_ids.append(i)
        except ValueError:
            invalid_count += 1
    result = _service.batch_delete(valid_ids)
    result["not_found"] += invalid_count
    return result

@router.get("/assets/{asset_id}")
def get_asset(asset_id: str):
    asset = _service.get_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="asset not found")
    return asset

# ========== SCAN APIs ==========
@router.get("/assets/{asset_id}/scan/dns")
def scan_dns(asset_id: str):
    asset = _service.get_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="asset not found")
    try:
        ip = socket.gethostbyname(asset.name)
        return {"asset_id": asset_id, "name": asset.name, "scan": "dns", "result": {"ip": ip}}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/assets/{asset_id}/scan/whois")
def scan_whois(asset_id: str):
    asset = _service.get_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="asset not found")
    try:
        w = whois.whois(asset.name)
        return {"asset_id": asset_id, "name": asset.name, "scan": "whois", "result": {
            "registrar": w.registrar,
            "creation_date": str(w.creation_date),
            "expiration_date": str(w.expiration_date),
        }}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/assets/{asset_id}/scan/ssl")
def scan_ssl(asset_id: str):
    asset = _service.get_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="asset not found")
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=asset.name) as s:
            s.connect((asset.name, 443))
            cert = s.getpeercert()
        return {"asset_id": asset_id, "name": asset.name, "scan": "ssl", "result": {
            "subject": dict(x[0] for x in cert["subject"]),
            "issuer": dict(x[0] for x in cert["issuer"]),
            "expire": cert["notAfter"],
        }}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/assets/{asset_id}/scan/port")
def scan_port(asset_id: str):
    asset = _service.get_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="asset not found")
    common_ports = [80, 443, 21, 22, 25, 3306, 5432, 8080]
    open_ports = []
    for port in common_ports:
        try:
            s = socket.socket()
            s.settimeout(1)
            if s.connect_ex((asset.name, port)) == 0:
                open_ports.append(port)
            s.close()
        except:
            pass
    return {"asset_id": asset_id, "name": asset.name, "scan": "port", "result": {"open_ports": open_ports}}