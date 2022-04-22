"""Config flow for melnor."""

from __future__ import annotations

import logging
from typing import Any

from melnor_bluetooth.device import Device
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_MAC, CONF_NAME
from homeassistant.data_entry_flow import AbortFlow, FlowResult

from .const import CONF_VALVE_COUNT, DISCOVER_SCAN_TIMEOUT, DOMAIN
from .discovery import async_discover_devices

_LOGGER = logging.getLogger(__name__)


def config_entry_name(device: Device) -> str:
    """Return the name of the config entry."""
    return f"{device.name} {device.mac}"


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for WiZ."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovered_device: Device
        self._discovered_devices: dict[str, Device]

    async def async_step_integration_discovery(
        self, discovery_info: dict[str, Any]
    ) -> FlowResult:
        """Handle integration discovery."""

        self._discovered_device = Device(
            discovery_info[CONF_MAC],
            discovery_info[CONF_NAME],
            False,
            discovery_info[CONF_VALVE_COUNT],
        )

        assert self._discovered_device is not None
        _LOGGER.debug("Discovered device: %s", self._discovered_device)

        await self.async_set_unique_id(discovery_info[CONF_MAC])
        self._abort_if_unique_id_configured(
            updates={CONF_MAC: discovery_info[CONF_MAC]}
        )

        return await self.async_step_discovery_confirm()

    async def _async_connect_discovered_or_abort(self) -> None:
        """Connect to the device and verify its responding."""

        try:
            await self._discovered_device.connect()
        except Exception as ex:
            _LOGGER.debug(
                "Failed to connect to %s during discovery: %s",
                self._discovered_device.mac,
                ex,
                exc_info=True,
            )
            raise AbortFlow("cannot_connect") from ex
        await self._discovered_device.disconnect()

    async def async_step_discovery_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm discovery."""
        assert self._discovered_device is not None

        device = self._discovered_device

        if user_input is not None:
            # Make sure the device is still there and test if we can connect to it
            await self._async_connect_discovered_or_abort()
            return self.async_create_entry(
                title=config_entry_name(device),
                data={
                    CONF_MAC: device.mac,
                    CONF_NAME: device.name,
                    CONF_VALVE_COUNT: device.valve_count,
                },
            )

        self._set_confirm_only()
        placeholders = {
            CONF_NAME: device.name,
            CONF_MAC: device.name,
            CONF_VALVE_COUNT: device.valve_count,
        }
        self.context["title_placeholders"] = placeholders
        return self.async_show_form(
            step_id="discovery_confirm",
            description_placeholders=placeholders,
        )

    async def async_step_pick_device(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the step to pick discovered device."""

        if user_input is not None:
            device = self._discovered_devices[user_input[CONF_MAC]]
            await self.async_set_unique_id(device.mac, raise_on_progress=False)
            return self.async_create_entry(
                title=config_entry_name(device),
                data={
                    CONF_MAC: device.mac,
                    CONF_NAME: device.name,
                    CONF_VALVE_COUNT: device.valve_count,
                },
            )

        current_unique_ids = self._async_current_ids()
        current_devices = {
            entry.data[CONF_MAC]
            for entry in self._async_current_entries(include_ignore=False)
        }

        self._discovered_devices = await async_discover_devices(DISCOVER_SCAN_TIMEOUT)

        device_macs = {
            mac
            for mac in self._discovered_devices.keys()
            if mac not in current_unique_ids and mac not in current_devices
        }

        if len(device_macs) == 1:
            mac = next(iter(device_macs))
            return await self.async_step_pick_device({CONF_MAC: mac})

        # # Check if there is at least one device
        if not device_macs:
            return self.async_abort(reason="no_devices_found")
        return self.async_show_form(
            step_id="pick_device",
            data_schema=vol.Schema({vol.Required(CONF_MAC): vol.In(device_macs)}),
        )

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle a flow initialized by the user."""
        return await self.async_step_pick_device()
