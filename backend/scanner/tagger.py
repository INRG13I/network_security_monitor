def normalize_os_name(raw_os, vendor=None):
    raw = raw_os.lower()
    vendor = (vendor or "").lower()

    if 'windows' in raw:
        return 'windows'
    if 'linux' in raw:
        return 'linux'
    if 'mac' in raw or 'darwin' in raw:
        return 'macos'
    if 'ios' in raw:
        return 'ios'
    if 'android' in raw and 'phone' in raw:
        return 'android'
    if 'android' in raw and 'huawei' in vendor:
        return 'linux'

    hardware_keywords = ['jetstream', 'switch', 'router', 'gateway', 'bridge', 'access point']
    if any(word in raw for word in hardware_keywords):
        return 'unknown'

    return 'unknown'


def guess_os_by_vendor(vendor_name):
    vendor_name = vendor_name.lower()

    vendor_os_map = {
        'android': ['samsung', 'xiaomi', 'huawei', 'oneplus', 'oppo', 'realme', 'google'],
        'ios': ['apple', 'ipad', 'iphone'],
        'windows': ['microsoft', 'hp', 'dell', 'lenovo', 'acer', 'asus'],
        'linux': ['raspberry', 'ubuntu', 'debian', 'intel'],
        'macos': ['macbook', 'imac'],
    }

    for os_name, vendors in vendor_os_map.items():
        if any(v in vendor_name for v in vendors):
            return os_name

    return 'unknown'


def tag_by_snmp(snmp_data):
    tags = set()
    if not snmp_data:
        return tags

    descr = snmp_data.get("sysDescr", "").lower()
    name = snmp_data.get("sysName", "").lower()
    object_id = snmp_data.get("sysObjectID", "")
    forwarding = snmp_data.get("ipForwarding")

    oid_map = {
        '1.3.6.1.4.1.9.1.516': 'switch',
        '1.3.6.1.4.1.9.1.241': 'router',
        '1.3.6.1.4.1.14988': 'router',
        '1.3.6.1.4.1.11.2.3.9': 'printer',
        '1.3.6.1.4.1.2636': 'router',
    }

    for oid_prefix, tag in oid_map.items():
        if object_id.startswith(oid_prefix):
            tags.add(tag)

    keywords = {
        "switch": ["switch", "jetstream", "smart switch", "edge", "gs108", "sfp"],
        "access point": ["access point", "aironet", "unifi", "wlan", "wireless"],
        "firewall": ["firewall", "palo alto", "fortinet", "checkpoint"],
        "server": ["vmware", "hyper-v", "server", "esxi"],
        "router": ["router"],
        "printer": ["printer"],
        "camera": ["camera"],
    }

    for tag, kw_list in keywords.items():
        if any(k in descr or k in name for k in kw_list):
            tags.add(tag)

    if forwarding == "1":
        tags.add("router")

    return tags


def tag_by_ports(device):
    tags = set()
    ports = device.get("ports", [])

    open_ports = [p for p in ports if p.get("status") == "open"]

    for p in open_ports:
        port = p.get("port")
        service = (p.get("service") or "").lower()
        product = (p.get("product") or "").lower()

        if port in [53, 67, 68, 161, 500, 4500] or service in ['dns', 'dhcp', 'snmp', 'ipsec', 'isakmp']:
            tags.add("router")

        if service in ['telnet', 'ssh', 'http'] and 'switch' in product:
            tags.add("switch")
        elif port in [22, 23, 80, 443] and 'switch' in product:
            tags.add("switch")

        if port in [1812, 1813, 16000] or service in ['radius'] or 'ap' in product:
            tags.add("access point")

        if port in [2049, 111, 445, 139] or service in ['smb', 'nfs', 'ftp', 'afp', 'cifs']:
            tags.add("nas")

        if port in [9100, 515, 631] or service in ['printer', 'ipp', 'jetdirect']:
            tags.add("printer")

        if port in [554, 8554, 37777] or service in ['rtsp', 'camera', 'video']:
            tags.add("camera")

        if port in [80, 443, 8080] or service in ['http', 'https']:
            tags.add("web interface")

        if port in [5060, 5061] or 'voip' in service:
            tags.add("voip")

        if port in [1883, 8883, 5683] or service in ['mqtt', 'coap']:
            tags.add("iot")

    return list(tags)


def tag_by_vendor_and_os(device):
    tags = set()
    vendor = device.get("vendor", "").lower()
    os_name = device.get("os", "").lower()

    if any(v in vendor for v in ['huawei', 'tp-link', 'cisco', 'zyxel', 'mikrotik', 'juniper']):
        tags.add("router")
    if any(v in vendor for v in ['epson', 'canon', 'brother', 'hp', 'lexmark']):
        tags.add("printer")
    if any(v in vendor for v in ['tuya', 'shelly', 'xiaomi', 'tplink smart']):
        tags.add("iot")
    if any(v in vendor for v in ['ubiquiti', 'engenius']) or os_name == "access point":
        tags.add("access point")
    if os_name in ['linux', 'windows', 'macos']:
        tags.add("computer")
    if os_name in ['android', 'ios']:
        tags.add("phone")

    return list(tags)


def assign_tags(device):
    device['os'] = normalize_os_name(device.get('os', ''), vendor=device.get('vendor'))
    if device['os'] == 'unknown' and device.get('vendor', 'unknown') != 'unknown':
        guessed = guess_os_by_vendor(device['vendor'])
        if guessed != 'unknown':
            device['os'] = guessed

    tags = set()
    tags.update(tag_by_ports(device))
    tags.update(tag_by_vendor_and_os(device))
    tags.update(tag_by_snmp(device.get("snmp", {})))

    device['tags'] = sorted(tags)
    return device
