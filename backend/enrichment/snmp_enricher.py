import subprocess
import re
from datetime import timedelta

from backend.utils.network_utils import run_snmpget_v2c, run_snmpget_v3
from config.ConfigLoader import ConfigLoader


def snmp_get_sysname_v2c(ip, community):
    oid = "1.3.6.1.2.1.1.5.0"  # sysName.0

    cmd = [
        "snmpget",
        "-v2c",
        "-c", community,
        ip,
        oid
    ]

    print("Running command:", " ".join(cmd))  # <-- Add this line

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
        if result.returncode == 0:
            line = result.stdout.strip()
            if "=" in line:
                return line.split("=", 1)[-1].replace("STRING:", "").strip()
            return line
        else:
            print(f"[SNMP error] {ip}: {result.stderr.strip()}")
    except Exception as e:
        print(f"[SNMP exception] {ip}: {e}")

    return "Unknown"

def snmp_get_sysname_v3(ip, username, auth_key, auth_protocol="SHA"):
    """
    Use net-snmp's CLI tool via subprocess to get sysName.0 from a device using SNMPv3.
    Supports SNMPv3 with authNoPriv mode. Compatible with Python 3.12+.

    Parameters
    ----------
    ip : str
        IP address of the SNMP device.
    username : str
        SNMPv3 username.
    auth_key : str
        SNMPv3 authentication key.
    auth_protocol : str
        Authentication protocol (default: "SHA"). Can also be "MD5".

    Returns
    -------
    str
        The sysName string from the SNMP agent, or "Unknown" on error.
    """
    oid = "1.3.6.1.2.1.1.5.0"  # sysName.0

    cmd = [
        "snmpget",
        "-v3",
        "-l", "authNoPriv",
        "-u", username,
        "-A", auth_key,
        "-a", auth_protocol,
        ip,
        oid
    ]

    print("Running command:", " ".join(cmd))  # Debug output

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
        if result.returncode == 0:
            line = result.stdout.strip()
            if "=" in line:
                return line.split("=", 1)[-1].replace("STRING:", "").strip()
            return line
        else:
            print(f"[SNMP error] {ip}: {result.stderr.strip()}")
    except Exception as e:
        print(f"[SNMP exception] {ip}: {e}")

    return "Unknown"

def snmp_get_uptime_v2c(ip, community):
    """
    Get sysUpTimeInstance via snmpget (v2c) and convert it to a timedelta.
    Handles various uptime formats, including very small uptimes.

    Parameters
    ----------
    ip : str
        IP address of SNMP device.
    community : str
        SNMP community string.

    Returns
    -------
    timedelta or None
        System uptime as timedelta, or None if error/unparseable.
    """
    oid = "1.3.6.1.2.1.1.3.0"

    cmd = [
        "snmpget",
        "-v2c",
        "-c", community,
        ip,
        oid
    ]

    print("Running command:", " ".join(cmd))

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
        if result.returncode != 0:
            print(f"[SNMP error] {ip}: {result.stderr.strip()}")
            return None

        line = result.stdout.strip()

        # Try pattern with days:
        m = re.search(r'(\d+)\s+day[s]?,\s*(\d+):(\d+):([\d.]+)', line)
        if m:
            days = int(m.group(1))
            hours = int(m.group(2))
            minutes = int(m.group(3))
            seconds = float(m.group(4))
            return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

        # Try pattern with hours:minutes:seconds:
        m = re.search(r'(\d+):(\d+):([\d.]+)', line)
        if m:
            hours = int(m.group(1))
            minutes = int(m.group(2))
            seconds = float(m.group(3))
            return timedelta(hours=hours, minutes=minutes, seconds=seconds)

        # Try pattern with only seconds (integer or float):
        m = re.search(r'Timeticks: \((\d+)\)', line)
        if m:
            # Timeticks are in hundredths of a second, convert to seconds
            timeticks = int(m.group(1))
            seconds = timeticks / 100
            return timedelta(seconds=seconds)

        print(f"[Parse error] Unexpected format: {line}")

    except Exception as e:
        print(f"[SNMP exception] {ip}: {e}")

    return None

def snmp_get_uptime_v3(ip, user, auth_key):
    """
    Get sysUpTimeInstance via snmpget (v3) and convert it to a timedelta.
    Handles various uptime formats, including very small uptimes.

    Parameters
    ----------
    ip : str
        IP address of SNMP device.
    user : str
        SNMPv3 username.
    auth_key : str
        SNMPv3 authentication key.

    Returns
    -------
    timedelta or None
        System uptime as timedelta, or None if error/unparseable.
    """
    oid = "1.3.6.1.2.1.1.3.0"

    cmd = [
        "snmpget",
        "-v3",
        "-l", "authNoPriv",
        "-u", user,
        "-A", auth_key,
        "-a", "SHA",
        ip,
        oid
    ]

    print("Running command:", " ".join(cmd))

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
        if result.returncode != 0:
            print(f"[SNMP error] {ip}: {result.stderr.strip()}")
            return None

        line = result.stdout.strip()

        # Try pattern with days:
        m = re.search(r'(\d+)\s+day[s]?,\s*(\d+):(\d+):([\d.]+)', line)
        if m:
            days = int(m.group(1))
            hours = int(m.group(2))
            minutes = int(m.group(3))
            seconds = float(m.group(4))
            return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

        # Try pattern with hours:minutes:seconds:
        m = re.search(r'(\d+):(\d+):([\d.]+)', line)
        if m:
            hours = int(m.group(1))
            minutes = int(m.group(2))
            seconds = float(m.group(3))
            return timedelta(hours=hours, minutes=minutes, seconds=seconds)

        # Try pattern with only timeticks (hundredths of seconds):
        m = re.search(r'Timeticks: \((\d+)\)', line)
        if m:
            timeticks = int(m.group(1))
            seconds = timeticks / 100
            return timedelta(seconds=seconds)

        print(f"[Parse error] Unexpected format: {line}")

    except Exception as e:
        print(f"[SNMP exception] {ip}: {e}")

    return None

def snmp_get_os_v2c(ip, community):
    """
    Extracts the software information from sysDescr using SNMPv2c.

    Parameters
    ----------
    ip : str
        IP address of the SNMP device.
    community : str
        SNMP community string.

    Returns
    -------
    str
        The string after 'Software:' in sysDescr, or 'Unknown' if not found.
    """
    oid = "1.3.6.1.2.1.1.1.0"  # sysDescr

    cmd = [
        "snmpget",
        "-v2c",
        "-c", community,
        ip,
        oid
    ]

    print("Running command:", " ".join(cmd))

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
        if result.returncode == 0:
            output = result.stdout.strip()

            # Extract the content after 'STRING:'
            match = re.search(r'STRING:\s*(.*)', output)
            if match:
                sysdescr = match.group(1)

                # Extract content after 'Software:'
                sw_match = re.search(r'Software:\s*(.*)', sysdescr)
                if sw_match:
                    return sw_match.group(1).strip()

                # If no 'Software:' found, return full sysDescr
                return sysdescr.strip()

            return "Unknown"
        else:
            print(f"[SNMP error] {ip}: {result.stderr.strip()}")
    except Exception as e:
        print(f"[SNMP exception] {ip}: {e}")

    return "Unknown"

def snmp_get_os_v3(ip, username, auth_key):
    """
    Extracts the software information from sysDescr using SNMPv3.

    Parameters
    ----------
    ip : str
        IP address of the SNMP device.
    username : str
        SNMPv3 username.
    auth_key : str
        SNMPv3 authentication password (SHA).

    Returns
    -------
    str
        The string after 'Software:' in sysDescr, or 'Unknown' if not found.
    """
    oid = "1.3.6.1.2.1.1.1.0"  # sysDescr

    cmd = [
        "snmpget",
        "-v3",
        "-l", "authNoPriv",
        "-u", username,
        "-A", auth_key,
        "-a", "SHA",
        ip,
        oid
    ]

    print("Running command:", " ".join(cmd))

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
        if result.returncode == 0:
            output = result.stdout.strip()

            # Extract the content after 'STRING:'
            match = re.search(r'STRING:\s*(.*)', output)
            if match:
                sysdescr = match.group(1)

                # Extract content after 'Software:'
                sw_match = re.search(r'Software:\s*(.*)', sysdescr)
                if sw_match:
                    return sw_match.group(1).strip()

                return sysdescr.strip()

            return "Unknown"
        else:
            print(f"[SNMP error] {ip}: {result.stderr.strip()}")
    except Exception as e:
        print(f"[SNMP exception] {ip}: {e}")

    return "Unknown"

def snmp_get_status_v2c(ip, community):
    """
    Uses SNMP to determine if a device is reachable (up).
    It tries to get sysUpTime OID. If successful, the device is up.

    Returns
    -------
    bool
        True if SNMP responds, False otherwise.
    """
    oid = "1.3.6.1.2.1.1.3.0"  # sysUpTime

    cmd = [
        "snmpget",
        "-v2c",
        "-c", community,
        ip,
        oid
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
        return result.returncode == 0
    except Exception:
        return False

def snmp_get_status_v3(ip, username, auth_key):
    """
    Checks if a device is up using SNMPv3 by querying sysUpTime.

    Parameters
    ----------
    ip : str
        Target device IP address.
    username : str
        SNMPv3 username.
    auth_key : str
        SNMPv3 authentication password (SHA).

    Returns
    -------
    bool
        True if the device responds to SNMPv3 query, False otherwise.
    """
    oid = "1.3.6.1.2.1.1.3.0"  # sysUpTime OID

    cmd = [
        "snmpget",
        "-v3",
        "-l", "authNoPriv",
        "-u", username,
        "-A", auth_key,
        "-a", "SHA",
        ip,
        oid
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
        return result.returncode == 0
    except Exception:
        return False

def get_in_octets_v2c(ip: str, index: int, community: str = 'public') -> int:
    """Retrieve ifInOctets for the given interface index."""
    oid = f'1.3.6.1.2.1.2.2.1.10.{index}'
    value = run_snmpget_v2c(ip, oid, community)
    return int(value)

def get_out_octets_v2c(ip: str, index: int, community: str = 'public') -> int:
    """Retrieve ifOutOctets for the given interface index."""
    oid = f'1.3.6.1.2.1.2.2.1.16.{index}'
    value = run_snmpget_v2c(ip, oid, community)
    return int(value)

def get_in_octets_v3(ip: str, index: int, username: str, auth_key: str, auth_protocol: str = "SHA") -> int:
    oid = f'1.3.6.1.2.1.2.2.1.10.{index}'
    return int(run_snmpget_v3(ip, oid, username, auth_key, auth_protocol))

def get_out_octets_v3(ip: str, index: int, username: str, auth_key: str, auth_protocol: str = "SHA") -> int:
    oid = f'1.3.6.1.2.1.2.2.1.16.{index}'
    return int(run_snmpget_v3(ip, oid, username, auth_key, auth_protocol))

def detect_snmp_version(ip: str) -> str | None:
    """Determine SNMP version supported by device."""
    config = ConfigLoader()
    v3 = config.get("snmp_v3", {})
    username = v3.get("username", "admin")
    auth_key = v3.get("auth_key", "admin123")
    auth_protocol = v3.get("auth_protocol", "SHA")

    test_oid = '1.3.6.1.2.1.1.1.0'  # sysDescr

    try:
        run_snmpget_v3(ip, test_oid, username, auth_key, auth_protocol)
        return "v3"
    except Exception:
        pass

    try:
        run_snmpget_v2c(ip, test_oid)
        return "v2c"
    except Exception:
        pass

    return None


def enrich_device_with_snmp(device):
    ip = device.get("ip")
    community = "public"

    config = ConfigLoader()
    v3_config = config.get("snmp_v3", {})
    user = v3_config.get("username", "admin")
    auth_key = v3_config.get("auth_key", "admin123")
    auth_protocol = v3_config.get("auth_protocol", "SHA")

    sysname = None
    uptime = None
    os = None
    snmp_detected = False

    # Check SNMPv3
    if snmp_get_status_v3(ip, user, auth_key):
        print(f"[+] SNMPv3 supported on {ip}")
        sysname = snmp_get_sysname_v3(ip, user, auth_key, auth_protocol)
        uptime = snmp_get_uptime_v3(ip, user, auth_key)
        os = snmp_get_os_v3(ip, user, auth_key)
        device["snmp_version"] = "v3"
        snmp_detected = True

    # Check SNMPv2c if v3 failed or incomplete
    elif snmp_get_status_v2c(ip, community):
        print(f"[+] SNMPv2c supported on {ip}")
        sysname = snmp_get_sysname_v2c(ip, community)
        uptime = snmp_get_uptime_v2c(ip, community)
        os = snmp_get_os_v2c(ip, community)
        device["snmp_version"] = "v2c"
        snmp_detected = True

    else:
        print(f"[!] No SNMP support detected on {ip}")
        device["snmp_version"] = None
        device["device_status"] = False
        return device

    # Update fields if detected
    if sysname:
        device["hostname"] = sysname
    if uptime:
        device["device_uptime"] = int(uptime.total_seconds())
    if os:
        device["os"] = os

    device["device_status"] = snmp_detected
    return device
