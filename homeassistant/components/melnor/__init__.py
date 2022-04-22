"""The melnor integration."""

import asyncio
import logging
from typing import Any

from melnor_bluetooth.device import Device

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_MAC, CONF_NAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import CONF_VALVE_COUNT, DISCOVER_SCAN_TIMEOUT, DISCOVERY_INTERVAL, DOMAIN
from .discovery import async_discover_devices
from .models import MelnorData, MelnorDataUpdateCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SWITCH]

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, hass_config: ConfigType) -> bool:
    """Set up the melnor integration."""

    async def _async_discovery(*_: Any) -> None:
        """Discover devices."""
        devices = await async_discover_devices(DISCOVER_SCAN_TIMEOUT)

        for device in devices.values():
            hass.async_create_task(
                hass.config_entries.flow.async_init(
                    DOMAIN,
                    context={"source": config_entries.SOURCE_INTEGRATION_DISCOVERY},
                    data={
                        CONF_MAC: device.mac,
                        CONF_NAME: device.name,
                        CONF_VALVE_COUNT: device.valve_count,
                    },
                )
            )

    asyncio.create_task(_async_discovery())
    async_track_time_interval(hass, _async_discovery, DISCOVERY_INTERVAL)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up melnor from a config entry."""
    hass.data.setdefault(DOMAIN, {}).setdefault(entry.entry_id, {})

    # Create the device, but do not connect yet. We'll do that later in the coordinator
    device = Device(
        entry.data[CONF_MAC],
        entry.data[CONF_NAME],
        False,
        entry.data[CONF_VALVE_COUNT],
    )

    coordinator: DataUpdateCoordinator[Device] = MelnorDataUpdateCoordinator(
        hass, device
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id]["data"] = MelnorData(coordinator, device)

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    await hass.data[DOMAIN][entry.entry_id]["data"].device.disconnect()

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
