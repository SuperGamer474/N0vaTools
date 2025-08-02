import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# Default ports to scan: 1-65535
COMMON_PORTS = list(range(1, 65536))

# Fallback map for common ports (likely services)
SERVICE_MAP = {
    21: "ftp",
    22: "ssh",
    23: "telnet",
    25: "smtp",
    53: "dns",
    80: "http",
    110: "pop3",
    135: "msrpc",
    139: "netbios-ssn",
    143: "imap",
    443: "https",
    445: "microsoft-ds",
    3389: "ms-wbt-server",
    3306: "mysql",
    5432: "postgresql",
    5900: "vnc",
    8000: "http",
    8080: "http"
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