import subprocess


def snmp_get_sysdescr(ip, v3_user=None, v3_auth_key=None, community="public"):
    """
    Use net-snmp's CLI tool via subprocess to get sysDescr from a device.
    Supports SNMPv3 and v2c. Works with Python 3.12.
    """
    oid = "1.3.6.1.2.1.1.1.0"

    # Prefer SNMPv3 if credentials are provided
    if v3_user and v3_auth_key:
        cmd = [
            "snmpwalk",
            "-v3",
            "-l", "authNoPriv",
            "-u", v3_user,
            "-A", v3_auth_key,
            "-a", "SHA",
            ip,
            oid
        ]
    else:
        # Fallback to SNMPv2c
        cmd = [
            "snmpwalk",
            "-v2c",
            "-c", community,
            ip,
            oid
        ]

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