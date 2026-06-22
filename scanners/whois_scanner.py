import whois

def scan_whois(domain: str) -> dict:
    try:
        w = whois.whois(domain)
        return {
            "domain": domain,
            "registrar": w.registrar,
            "creation_date": str(w.creation_date),
            "expiration_date": str(w.expiration_date),
            "name_servers": w.name_servers,
        }
    except Exception as e:
        return {"domain": domain, "error": str(e)}