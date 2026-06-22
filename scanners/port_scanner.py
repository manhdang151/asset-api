import socket

def scan_port(host: str) -> dict:
    common_ports = {
        21: "FTP", 22: "SSH", 25: "SMTP", 53: "DNS",
        80: "HTTP", 443: "HTTPS", 3306: "MySQL",
        5432: "PostgreSQL", 8080: "HTTP-Alt", 8443: "HTTPS-Alt"
    }
    open_ports = []
    for port, service in common_ports.items():
        try:
            s = socket.socket()
            s.settimeout(1)
            if s.connect_ex((host, port)) == 0:
                open_ports.append({"port": port, "service": service})
            s.close()
        except:
            pass
    return {"host": host, "open_ports": open_ports}