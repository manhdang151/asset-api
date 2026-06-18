import dns.resolver


def scan_dns(domain: str) -> dict:
    """Lookup các DNS record cơ bản: A, MX, NS"""
    records = {}

    for record_type in ["A", "MX", "NS"]:
        try:
            answers = dns.resolver.resolve(domain, record_type)
            records[record_type] = [str(rdata) for rdata in answers]
        except Exception:
            records[record_type] = []

    return {"domain": domain, "records": records}