import ssl
import socket

def scan_ssl(domain: str) -> dict:
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
            s.settimeout(5)
            s.connect((domain, 443))
            cert = s.getpeercert()
        return {
            "domain": domain,
            "subject": dict(x[0] for x in cert["subject"]),
            "issuer": dict(x[0] for x in cert["issuer"]),
            "version": cert.get("version"),
            "expire": cert["notAfter"],
            "san": cert.get("subjectAltName", []),
        }
    except Exception as e:
        return {"domain": domain, "error": str(e)}