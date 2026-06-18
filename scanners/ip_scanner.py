import requests


def scan_ip(ip_address: str) -> dict:
    """Lấy thông tin geolocation và ASN của 1 IP"""
    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}", timeout=5)
        data = response.json()

        if data.get("status") == "fail":
            return {"ip_address": ip_address, "error": data.get("message", "lookup failed")}

        return {
            "ip_address": ip_address,
            "geolocation": {
                "country": data.get("country"),
                "country_code": data.get("countryCode"),
                "city": data.get("city"),
                "region": data.get("regionName"),
                "latitude": data.get("lat"),
                "longitude": data.get("lon"),
                "isp": data.get("isp"),
                "org": data.get("org"),
            },
            "asn": {
                "number": data.get("as", "").split()[0].replace("AS", "") if data.get("as") else None,
                "name": data.get("as"),
            },
        }
    except Exception as e:
        return {"ip_address": ip_address, "error": str(e)}