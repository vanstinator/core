"""melnor integration models."""

from dataclasses import dataclass
from datetime import timedelta
import logging

import async_timeout
from melnor_bluetooth.device import Device

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass
class MelnorData:
    """Data for the melnor integration."""

    coordinator: DataUpdateCoordinator
    device: Device


class MelnorDataUpdateCoordinator(DataUpdateCoordinator):
    """Melnor data update coordinator."""

    _is_connected: bool = False

    def __init__(self, hass: HomeAssistant, device: Device) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="Melnor Bluetooth Watering Valve",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=10),
        )
        self._device = device

    _is_connected = False

    async def _async_update_data(self) -> Device:
        """Update data."""

        # The bluetooth wrapper handles exceptions for us.
        # We just need to check the connection state and attempt to self-heal the connection if it drops.
        if not self._device.is_connected:

            if self._is_connected:
                self._is_connected = False
                _LOGGER.warning("%s has disconnected", self._device.mac)

            async with async_timeout.timeout(10):
                await self._device.connect()
        else:
            await self._device.fetch_state()

        if self._device.is_connected and not self._is_connected:
            self._is_connected = True
            _LOGGER.debug("%s has re-connected", self._device.mac)

        return self._device


class MelnorBluetoothBaseEntity(CoordinatorEntity):
    """Base class for melnor entities."""

    _coordinator: DataUpdateCoordinator[Device]
    _device: Device

    def __init__(
        self,
        data: MelnorData,
    ) -> None:
        """Initialize a melnor base entity."""
        super().__init__(data.coordinator)
        self._coordinator = data.coordinator
        self._device = data.device

    @property
    def name(self):
        """Return the name of the device."""
        return self._device.name

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"{self.device.mac}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.device.mac)},
            model=self.device.model,
            name=self.device.name,
            manufacturer="Melnor",
        )

    @property
    def device(self) -> Device:
        """Return the device."""
        return self._device
