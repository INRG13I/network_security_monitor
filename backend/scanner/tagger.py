def normalize_os_name(raw_os, vendor=None):
    """Clean and standardize OS labels, avoiding hardware model confusion."""
    raw = raw_os.lower()
    vendor = (vendor or "").lower()

    # Known OS names
    if 'windows' in raw:
        return 'Windows'
    if 'linux' in raw:
        return 'Linux'
    if 'mac' in raw or 'darwin' in raw:
        return 'macOS'
    if 'ios' in raw:
        return 'iOS'
    if 'android' in raw and 'phone' in raw:
        return 'Android'

    # Fix Huawei router misclassification
    if 'android' in raw and 'huawei' in vendor:
        return 'Linux'

    # Device model strings are not OS
    hardware_words = ['jetstream', 'switch', 'router', 'gateway', 'bridge', 'access point']
    if any(word in raw for word in hardware_words):
        return 'Unknown'

    return 'Unknown'



def tag_by_device_type(device):
    """Assign device type tags based on vendor, OS, model hints, and open ports."""
    tags = []
    vendor = device.get('vendor', '').lower()
    os = device.get('os', '').lower()
    ports = [p['port'] for p in device.get('ports', [])]
    descr = device.get('os', '').lower()  # using OS to hold sysDescr-like info

    # Vendor-based hints
    if 'huawei' in vendor:
        tags.append('Router')
    if 'tp-link' in vendor:
        if 'jetstream' in descr or 'switch' in descr:
            tags.append('Switch')
        else:
            tags.append('Router')

    if any(v in vendor for v in ['cisco', 'zyxel', 'mikrotik']):
        tags.append('Router')
    if any(v in vendor for v in ['hp', 'epson', 'canon', 'brother']):
        tags.append('Printer')
    if any(v in vendor for v in ['tuya', 'shelly', 'sonoff', 'tplink smart']):
        tags.append('IoT')

    # Port-based hinting
    if any(p in ports for p in [53, 80, 443]) and 'Router' not in tags:
        tags.append('Web')
    if any(p in ports for p in [1883, 5683]):
        tags.append('IoT')

    # OS-based tagging
    if os in ['android', 'ios']:
        tags.append('Phone')
    if os in ['linux', 'windows', 'macos'] and not tags:
        tags.append('Computer')

    return list(set(tags))





def tag_by_os(device):
    """Return OS tags based on device's OS."""
    os_name = device['os'].lower()
    os_tags = {
        "android": "Android",
        "ios": "iOS",
        "windows": "Windows",
        "linux": "Linux",
        "macos": "macOS"
    }

    tags = []
    for key, tag in os_tags.items():
        if key in os_name:
            tags.append(tag)
            # Tag as phone if Android or iOS
            if tag in ["Android", "iOS"]:
                tags.append("Phone")
    return tags


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
            return os_name.capitalize()

    return 'Unknown'


def tag_by_vendor(device):
    """Return vendor-based tags."""
    vendor_name = device['vendor'].lower()
    tags = []

    router_vendors = ['huawei', 'tp-link', 'cisco']
    printer_vendors = ['hp', 'epson', 'brother', 'canon']
    iot_vendors = ['tuya', 'xiaomi', 'shelly']

    if any(vendor in vendor_name for vendor in router_vendors):
        tags.append("Router")
    if any(vendor in vendor_name for vendor in printer_vendors):
        tags.append("Printer")
    if any(vendor in vendor_name for vendor in iot_vendors):
        tags.append("IoT")

    return tags


def tag_by_ports(device):
    """Return port-based tags."""
    tags = []
    common_router_ports = [53, 80, 443]
    iot_ports = [1883, 5683]

    if any(port['port'] in common_router_ports for port in device['ports']):
        tags.append("Router")
    if any(port['port'] in iot_ports for port in device['ports']):
        tags.append("IoT")

    return tags


def assign_tags(device):
    """Assign tags and normalize OS for the given device."""
    device['os'] = normalize_os_name(device.get('os', ''), vendor=device.get('vendor'))

    if device['os'] == 'Unknown' and device['vendor'] != 'Unknown':
        guessed = guess_os_by_vendor(device['vendor'])
        if guessed != 'Unknown':
            device['os'] = guessed

    device['tags'] = sorted(set(tag_by_device_type(device)))
    return device
