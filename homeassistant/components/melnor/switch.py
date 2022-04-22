"""Support for Melnor RainCloud sprinkler water timer."""

from __future__ import annotations

from melnor_bluetooth.device import Valve

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .models import MelnorBluetoothBaseEntity, MelnorData


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_devices: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    switches = []

    data: MelnorData = hass.data[DOMAIN][config_entry.entry_id]["data"]

    device = data.device

    # This device may not have 4 valves total, but the library will only expose the right number of valves
    for i in range(1, 5):
        valve = device[f"zone{i}"]
        if valve is not None:
            switches.append(MelnorSwitch(hass, data, valve))

    async_add_devices(switches, True)


class MelnorSwitch(MelnorBluetoothBaseEntity, SwitchEntity):
    """A switch implementation for raincloud device."""

    _hass: HomeAssistant
    _valve: Valve

    def __init__(
        self,
        hass: HomeAssistant,
        data: MelnorData,
        valve: Valve,
    ) -> None:
        """Initialize a switch for raincloud device."""
        super().__init__(data)
        self._hass = hass
        self._valve = valve

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return super().device.is_connected

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._valve.is_watering

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        self._valve.is_watering = True
        await self.device.push_state()
        self._coordinator.async_set_updated_data(self.device)

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        self._valve.is_watering = False
        await self.device.push_state()
        self._coordinator.async_set_updated_data(self.device)

    @property
    def icon(self) -> str | None:
        """Return the icon."""
        return "mdi:sprinkler"

    @property
    def name(self):
        """Return the name of the switch."""
        return f"{self._device.name} Zone {self._valve.id+1}"

    @property
    def unique_id(self):
        """Return the unique id of the switch."""
        return super().unique_id + f"-zone{self._valve.id}"
