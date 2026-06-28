from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from service.scan_service import ScanService

router = APIRouter()

_service: ScanService = None


def set_service(service: ScanService):
    global _service
    _service = service


class StartScanBody(BaseModel):
    scan_type: str


# ========== POST /assets/{id}/scan ==========
@router.post("/assets/{asset_id}/scan", status_code=202)
def start_scan(asset_id: str, body: StartScanBody):
    try:
        job = _service.start_scan(asset_id, body.scan_type)
        return job
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ========== GET /scan-jobs/{id} ==========
@router.get("/scan-jobs/{job_id}")
def get_scan_job(job_id: str):
    job = _service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="scan job not found")
    return job


# ========== GET /scan-jobs/{id}/results ==========
@router.get("/scan-jobs/{job_id}/results")
def get_scan_results(job_id: str):
    try:
        return _service.get_results(job_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ========== GET /assets/{id}/scans ==========
@router.get("/assets/{asset_id}/scans")
def list_scans_for_asset(asset_id: str):
    return _service.get_scans_for_asset(asset_id)