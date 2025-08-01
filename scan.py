# scan.py
import os
import socket
import ipaddress
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from ping3 import ping as ping3
from nmb.NetBIOS import NetBIOS

def get_local_ip():
    """Returns the machine's LAN IP or None if not found."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return None
    finally:
        s.close()

def get_prefix_from_ipconfig(ip):
    """Gets subnet prefix length from ipconfig output."""
    try:
        output = subprocess.check_output("ipconfig", encoding="utf-8")
        pattern = rf"IPv4 Address.*?: {re.escape(ip)}.*?Subnet Mask.*?: ([\d.]+)"
        match = re.search(pattern, output, re.DOTALL)
        if match:
            mask = match.group(1)
            return sum(bin(int(octet)).count("1") for octet in mask.split('.'))
    except Exception:
        return 24  # fallback

def scan_via_netbios(code: str, timeout: float = 3.0):
    """Scan using NetBIOS protocol."""
    bios = NetBIOS(broadcast=True)
    ips = bios.queryName('*', ip='', timeout=timeout) or []
    found = None

    for ip in ips:
        names = bios.queryIPForName(ip, timeout=timeout)
        if names and code.lower() in names[0].lower():
            found = (ip, names[0])
            break

    bios.close()
    return found

def scan_via_icmp(code: str, hosts: list[str], timeout: float = 0.2):
    """Scan using ICMP ping and reverse DNS."""
    workers = min(len(hosts), os.cpu_count() * 10)
    with ThreadPoolExecutor(max_workers=workers) as exec:
        futures = {exec.submit(ping3, ip, timeout): ip for ip in hosts}

        for future in as_completed(futures):
            ip = futures[future]
            try:
                if future.result() is not None:  # host is alive
                    try:
                        name = socket.gethostbyaddr(ip)[0].lower()
                    except Exception:
                        name = ""
                    if code.lower() in name or code.lower() in ip.lower():
                        return ip, name or ip
            except Exception:
                continue
    return None

def scan(code: str):
    """
    Main scanning function that combines all methods.
    Returns (ip, name) if found, None otherwise.
    """
    local_ip = get_local_ip()
    if not local_ip:
        return None

    prefix = get_prefix_from_ipconfig(local_ip)
    network = ipaddress.ip_network(f"{local_ip}/{prefix}", strict=False)
    hosts = [str(h) for h in network.hosts()]

    # Try NetBIOS first
    result = scan_via_netbios(code, timeout=2.0)
    if result:
        return result

    # Fall back to ICMP scan
    return scan_via_icmp(code, hosts, timeout=0.2)