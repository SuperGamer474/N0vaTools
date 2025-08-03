import os
import socket
import ipaddress
import subprocess
import re
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from ping3 import ping as ping3

# === COMMON PORTS TO SCAN ===
COMMON_PORTS = list(range(1, 65536))

# === CONFIGURATION ===
MAX_IP_CONCURRENT = 5        # Max IPs to scan in parallel
MAX_PORT_THREADS = 1000      # Max threads per IP portscan
PORT_TIMEOUT = 0.7           # Seconds
PING_TIMEOUT = 0.5           # Seconds


def get_local_ip():
    """Get this machine's local LAN IP."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return None
    finally:
        s.close()


def get_prefix_from_ipconfig(ip):
    """Get subnet prefix length (like /24) from ipconfig."""
    try:
        output = subprocess.check_output("ipconfig", encoding="utf-8")
        pattern = rf"IPv4 Address.*?: {re.escape(ip)}.*?Subnet Mask.*?: ([\d.]+)"
        match = re.search(pattern, output, re.DOTALL)
        if match:
            mask = match.group(1)
            return sum(bin(int(octet)).count("1") for octet in mask.split('.'))
    except Exception:
        pass
    return 24  # fallback


def scan_port(target_ip, port, open_ports):
    """Try to connect to a port; if open, record it."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(PORT_TIMEOUT)
    try:
        s.connect((target_ip, port))
        open_ports.append(port)
    except:
        pass
    finally:
        s.close()


def portscan(target_ip):
    """Scan all ports on a single IP using a pool of threads."""
    open_ports = []
    desc = f"Ports @ {target_ip}"
    with ThreadPoolExecutor(max_workers=MAX_PORT_THREADS) as executor:
        futures = [executor.submit(scan_port, target_ip, port, open_ports) for port in COMMON_PORTS]
        for _ in tqdm(as_completed(futures), total=len(COMMON_PORTS), unit="ports", colour="magenta", ascii=False, leave=False, desc=desc):
            pass
    return sorted(open_ports)


def fullscan(filename):
    # 1️⃣ Determine network
    local_ip = get_local_ip()
    if not local_ip:
        print("❌ Could not get local IP. Aborting.")
        return

    prefix = get_prefix_from_ipconfig(local_ip)
    network = ipaddress.ip_network(f"{local_ip}/{prefix}", strict=False)
    hosts = [str(ip) for ip in network.hosts()]

    # 2️⃣ Ping sweep to find alive hosts
    print(f"🌐 Ping sweeping {network}...")
    alive = []
    with ThreadPoolExecutor(max_workers=os.cpu_count() * 10) as ping_executor:
        futures = {ping_executor.submit(ping3, ip, timeout=PING_TIMEOUT): ip for ip in hosts}
        for future in tqdm(as_completed(futures), total=len(hosts), unit="ips", colour="cyan", ascii=False, desc="Pinging"):
            ip = futures[future]
            try:
                if future.result() is not None:
                    try:
                        name = socket.gethostbyaddr(ip)[0]
                    except:
                        name = ip
                    alive.append((ip, name))
            except:
                pass

    if not alive:
        print("🚫 No live hosts found.")
        return

    # 3️⃣ Concurrent port scans on alive hosts
    print(f"🔍 Port scanning {len(alive)} hosts with up to {MAX_IP_CONCURRENT} parallel scans...")
    results = {}
    master_pbar = tqdm(total=len(alive), unit="hosts", colour="green", ascii=False, desc="Scanning IPs")

    def scan_host(entry):
        ip, name = entry
        ports = portscan(ip)
        results[ip] = {"name": name, "open_ports": ports}
        master_pbar.update(1)

    with ThreadPoolExecutor(max_workers=MAX_IP_CONCURRENT) as ip_executor:
        ip_executor.map(scan_host, alive)

    master_pbar.close()

    # 4️⃣ Save
    first = str(list(network.hosts())[0])
    last = str(list(network.hosts())[-1])
    results["ip_range"] = f"{first} - {last}"

    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"✅ Done! Results saved to: {filename}")


if __name__ == "__main__":
    fullscan("results.json")
