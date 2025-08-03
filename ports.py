import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# Default ports to scan: 1-65535
COMMON_PORTS = list(range(1, 65536))

# Fallback map for common ports (likely services)
SERVICE_MAP = {
    20: "ftp-data",          # Official IANA
    21: "ftp",               # Official IANA
    22: "ssh",               # Official IANA (SFTP runs over SSH here!)
    23: "telnet",            # Official IANA
    25: "smtp",              # Official IANA
    43: "whois",             # Official IANA
    53: "domain",            # Official IANA (DNS)
    67: "bootps",            # Official IANA (DHCP server)
    68: "bootpc",            # Official IANA (DHCP client)
    69: "tftp",              # Official IANA
    79: "finger",            # Official IANA
    80: "http",              # Official IANA
    110: "pop3",             # Official IANA
    # 115 reserved, no official assignment
    119: "nntp",             # Official IANA
    123: "ntp",              # Official IANA
    137: "netbios-ns",       # Official IANA
    138: "netbios-dgm",      # Official IANA
    139: "netbios-ssn",      # Official IANA
    389: "ldap",             # Official IANA
    443: "https",            # Official IANA
    445: "microsoft-ds",     # Official IANA
    465: "smtps",            # Official IANA (secure SMTP)
    587: "submission",       # Official IANA (modern SMTP submission)
    636: "ldaps",            # Official IANA (secure LDAP)
    # 689 unassigned by IANA
    989: "ftps-data",        # Official IANA (FTP over TLS/SSL data)
    990: "ftps",             # Official IANA (FTP over TLS/SSL control)
    992: "telnets",          # Official IANA (Telnet over TLS/SSL)
    993: "imaps",            # Official IANA (IMAP over SSL)
    995: "pop3s",            # Official IANA (POP3 over SSL)
    1433: "ms-sql-s",        # Microsoft SQL Server (commonly used)
    1434: "ms-sql-m",        # Microsoft SQL Server (commonly used)
    1521: "oracle",          # Oracle DB default port (common usage)
    1723: "pptp",            # Official IANA (VPN protocol)
    2049: "nfs",             # Official IANA (Network File System)
    3306: "mysql",           # Official IANA
    3389: "ms-wbt-server",   # Official IANA (RDP)
    5432: "postgresql",      # Official IANA
    5900: "vnc",             # Official IANA
    6379: "redis",           # Popular, not IANA assigned
    8000: "http-alt",        # Common unofficial HTTP alt port
    8080: "http-alt",        # Common unofficial HTTP alt port
    8443: "https-alt",       # Common unofficial HTTPS alt port
    8888: "http-alt",        # Common unofficial HTTP alt port
    27017: "mongodb",        # Popular, not IANA assigned
    # The following are NOT officially assigned by IANA but widely used:
    9000: "sonarqube",       # SonarQube web UI port
    9090: "webmin/prometheus", # Webmin or Prometheus web UI port
    10000: "webmin",         # Webmin web interface port
    11211: "memcached",      # Memcached port, widely used but unassigned by IANA
}

def scan_port(target_ip, port, results):
    """
    Attempt to connect to a single port and record if it's open.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.7)
    try:
        s.connect((target_ip, port))
        results.append(port)
    except:
        pass
    finally:
        s.close()


def portscan(target, ports=COMMON_PORTS, workers=1000):
    """
    Scans the given target for open TCP ports and prints each with its service name.
    Uses dynamic lookup first, then a fallback map for likely services.
    Shows a live progress bar (ascii=False).
    """
    print(f"\n🚀 Starting portscan on {target} (ports {ports[0]}-{ports[-1]})...")
    print()
    start = time.time()

    results = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(scan_port, target, port, results): port for port in ports}
        for _ in tqdm(as_completed(futures), total=len(ports), unit="ips", colour="cyan", ascii=False, leave=False, desc="Scanning ports"):
            pass

    open_ports = sorted(results)

    # Display open ports with service confidence
    for p in open_ports:
        svc = None
        certainty = ""
        try:
            svc = socket.getservbyport(p, 'tcp')
        except OSError:
            if p in SERVICE_MAP:
                svc = SERVICE_MAP[p]
                certainty = "Likely "
        if svc:
            print(f"Port {p} ({certainty}{svc}) is open")
        else:
            print(f"Port {p} is open")

    elapsed = time.time() - start
    print(f"\n✅ portscan done in {elapsed:.2f}s. Found {len(open_ports)} open ports.\n")