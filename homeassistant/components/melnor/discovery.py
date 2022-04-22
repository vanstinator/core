"""Discovery helpers for melnor."""

from melnor_bluetooth.device import Device
from melnor_bluetooth.scanner import scanner


async def async_discover_devices(timeout: int) -> dict[str, Device]:
    """Discover devices."""

    devices: dict[str, Device] = {}

    def _callback(device: Device):

        devices[device.mac] = device

    await scanner(_callback, scan_timeout_seconds=timeout)

    return devices
