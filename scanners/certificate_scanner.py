import ssl
import socket

def scan_certificate(domain: str) -> dict:
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
            s.settimeout(5)
            s.connect((domain, 443))
            cert = s.getpeercert()
        return {
            "domain": domain,
            "serial_number": cert.get("serialNumber"),
            "not_before": cert.get("notBefore"),
            "not_after": cert.get("notAfter"),
            "issuer": dict(x[0] for x in cert["issuer"]),
            "subject": dict(x[0] for x in cert["subject"]),
            "signature_algorithm": cert.get("signatureAlgorithm"),
        }
    except Exception as e:
        return {"domain": domain, "error": str(e)}