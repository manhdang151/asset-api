import requests

def scan_technical(domain: str) -> dict:
    try:
        url = f"https://{domain}"
        r = requests.get(url, timeout=5, verify=False)
        headers = dict(r.headers)
        techs = []

        server = headers.get("Server", "")
        if server:
            techs.append({"name": "Server", "value": server})

        powered = headers.get("X-Powered-By", "")
        if powered:
            techs.append({"name": "X-Powered-By", "value": powered})

        content_type = headers.get("Content-Type", "")
        if "wordpress" in r.text.lower():
            techs.append({"name": "CMS", "value": "WordPress"})
        if "drupal" in r.text.lower():
            techs.append({"name": "CMS", "value": "Drupal"})
        if "jquery" in r.text.lower():
            techs.append({"name": "JavaScript", "value": "jQuery"})
        if "react" in r.text.lower():
            techs.append({"name": "JavaScript", "value": "React"})
        if "nginx" in server.lower():
            techs.append({"name": "Web Server", "value": "Nginx"})
        if "apache" in server.lower():
            techs.append({"name": "Web Server", "value": "Apache"})

        return {
            "domain": domain,
            "status_code": r.status_code,
            "technologies": techs,
            "headers": {k: v for k, v in headers.items()
                       if k in ["Server", "X-Powered-By", "Content-Type", "X-Frame-Options"]}
        }
    except Exception as e:
        return {"domain": domain, "error": str(e)}