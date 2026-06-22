from model.scan_job import ScanJob, new_scan_job, VALID_SCAN_TYPES
from storage.scan_storage import ScanJobStorage
from storage.postgres_asset_storage import PostgresAssetStorage
from scanners.dns_scanner import scan_dns
from scanners.ip_scanner import scan_ip
from scanners.whois_scanner import scan_whois
from scanners.ssl_scanner import scan_ssl
from scanners.certificate_scanner import scan_certificate
from scanners.port_scanner import scan_port
from scanners.technical_scanner import scan_technical
from datetime import datetime, timezone


class ScanService:
    def __init__(self, scan_storage: ScanJobStorage, asset_storage: PostgresAssetStorage):
        self._scan_storage = scan_storage
        self._asset_storage = asset_storage

    def start_scan(self, asset_id: str, scan_type: str) -> ScanJob:
        if scan_type not in VALID_SCAN_TYPES:
            raise ValueError(f"invalid scan_type '{scan_type}', must be one of: {', '.join(VALID_SCAN_TYPES)}")

        asset = self._asset_storage.get_by_id(asset_id)
        if not asset:
            raise ValueError(f"asset '{asset_id}' not found")

        job = new_scan_job(asset_id, scan_type)
        self._scan_storage.create(job)
        self._run_scan(job, asset.name)

        return job

    def _run_scan(self, job: ScanJob, target: str) -> None:
        job.status = "running"
        job.started_at = datetime.now(timezone.utc)
        self._scan_storage.update(job)

        try:
            if job.scan_type == "dns":
                result = scan_dns(target)
            elif job.scan_type == "ip":
                result = scan_ip(target)
            elif job.scan_type == "whois":
                result = scan_whois(target)
            elif job.scan_type == "ssl":
                result = scan_ssl(target)
            elif job.scan_type == "certificate":
                result = scan_certificate(target)
            elif job.scan_type == "port":
                result = scan_port(target)
            elif job.scan_type == "technical":
                result = scan_technical(target)
            else:
                raise NotImplementedError(f"scan_type '{job.scan_type}' chưa được implement")

            job.results = [result]
            job.status = "completed"
        except Exception as e:
            job.status = "failed"
            job.error = str(e)

        job.ended_at = datetime.now(timezone.utc)
        self._scan_storage.update(job)

    def get_job(self, job_id: str) -> ScanJob | None:
        return self._scan_storage.get_by_id(job_id)

    def get_results(self, job_id: str) -> dict:
        job = self._scan_storage.get_by_id(job_id)
        if not job:
            raise ValueError("scan job not found")
        return {
            "job_id": job.id,
            "scan_type": job.scan_type,
            "results": job.results,
        }

    def get_scans_for_asset(self, asset_id: str) -> list[ScanJob]:
        return self._scan_storage.get_by_asset_id(asset_id)