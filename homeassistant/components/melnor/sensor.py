"""Support for Melnor RainCloud sprinkler water timer."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
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
    """Set up the sensor platform."""
    sensors = []

    data: MelnorData = hass.data[DOMAIN][config_entry.entry_id]["data"]

    sensors.append(MelnorSensor(hass, data))

    async_add_devices(sensors, True)


class MelnorSensor(MelnorBluetoothBaseEntity, SensorEntity):
    """A switch implementation for raincloud device."""

    _hass: HomeAssistant

    def __init__(
        self,
        hass: HomeAssistant,
        melnor_data: MelnorData,
    ) -> None:
        """Initialize a switch for raincloud device."""
        super().__init__(melnor_data)
        self._hass = hass

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return super().device.is_connected

    @property
    def device_class(self) -> str | None:
        """Return the device class."""
        return "battery"

    @property
    def native_value(self):
        """Return the battery level."""
        return self.device.battery_level

    @property
    def state_class(self):
        """Return the state of the entity."""
        return "measurement"

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return "%"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._device.name} Battery Level"

    @property
    def unique_id(self):
        """Return a unique ID."""
        return super().unique_id + "-battery"
